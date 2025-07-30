import json
import logging
import uuid
from typing import Any

from django.db.models import F
from django.db.transaction import atomic
from requests import RequestException
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotification

from config import settings
from finance.exceptions import (
    ApplicationRefillNotFoundError,
    PaymentIdExtractionError,
    YookassaPaymentCreateError,
    YookassaPaymentFinalizeError,
    YookassaPaymentStatusCheckError,
    YookassaPyamentConfirmationError,
    YookassaWebhookDataStructureError,
    YookassaWebhookJsonDecodeError,
    YookassaWebhookUnexpectedError,
)
from finance.models import Account, Application, ApplicationLog

logger = logging.getLogger("__name__")


def set_yookassa_configuration() -> None:
    """Задаем параметры Yookassa"""

    Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_application(serializer: Serializer, request: Request) -> dict[str, Any]:
    """
    Создание завяки на зачисление средств на баланс обменника с банковской карты
    через сервис YOOKASSA
    """

    set_yookassa_configuration()

    # создаем обьект заявки
    account_id = Account.objects.filter(
        сurrency=serializer.validated_data["currency"],
        user=request.user
    ).values_list("id", flat=True)[0]
    application = serializer.save(status=Application.PENDING, account_id=account_id)

    # создаем заявку на оплату на внешнем сервисе
    try:
        payment = Payment.create(
            {
                "amount": {
                    "value": str(serializer.validated_data.get("amount")),
                    "currency": "RUB",
                },
                "payment_method_data": {"type": "bank_card"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": settings.YOOKASSA_RETURN_URL,
                },
                "description": f"Заявка №{application.id} на пополнение счета ",
            },
            str(uuid.uuid4()),
        )
    except RequestException as error:
        logger.error(msg={"Yookassa API error: Payment creation failed": error})
        Application.objects.filter(id=application.id).update(status=Application.ERROR)
        raise YookassaPaymentCreateError(error) from error

    Application.objects.filter(id=application.id).update(
        payment_id=payment.payment_method.id
    )
    return {
        "confirmation_url": payment.confirmation.confirmation_url,
        "payment_id": payment.payment_method.id,
    }


def handle_yookassa_webhook(request: Request) -> None:
    """Обработка вебхука от YOOKASSA и подтверждение входящего платежа"""

    payment_id = handle_yookassa_webhook_notification(request=request)
    payment_confirmation(payment_id=payment_id)


def handle_yookassa_webhook_notification(request: Request) -> uuid:
    """Обработка Yookassa Webhook Notification  и получение из него payment_id"""

    set_yookassa_configuration()
    event_json = json.loads(request.body)

    try:
        notification_object = WebhookNotification(event_json)
        logging.info("Successfully parsed Yookassa webhook")

    except json.JSONDecodeError as error:
        logging.error(
            msg={"JSONDecodeError: Failed to parse Yookassa webhook JSON:": error}
        )
        raise YookassaWebhookJsonDecodeError(error) from error
    except (TypeError, ValueError) as error:
        logging.error(msg={"Invalid Yookassa webhook data structure": error})
        raise YookassaWebhookDataStructureError(error) from error
    except Exception as error:
        # Общий перехват для любых других неожиданных ошибок
        logging.critical(
            msg={"Unexpected error during Yookassa webhook processing:": error}
        )
        raise YookassaWebhookUnexpectedError(error) from error

    try:
        payment_id = notification_object.object.id
    except AttributeError as error:
        logging.critical(
            msg={
                "Invalid notification object structure for paymentID extraction": error
            }
        )
        raise PaymentIdExtractionError(error) from error

    return payment_id


def payment_confirmation(payment_id: uuid):
    """Подтверждение платежа"""

    if not Application.objects.filter(payment_id=payment_id).exists():
        logger.error(f"Заявка на ввод платежа {payment_id} не найдена")
        raise ApplicationRefillNotFoundError(payment_id)

    application = Application.objects.get(payment_id=payment_id)

    try:
        Payment.capture( # подтверждаем платеж
            payment_id,
            {
                "amount": {
                    "value": str(application.amount),
                    "currency": "RUB",
                },
            },
            str(uuid.uuid4()),
        )
    except RequestException as error:
        logger.error(
            msg={f"Failed to confirm payment {payment_id} with Yookassa: {error}"}
        )
        raise YookassaPyamentConfirmationError(payment_id, error) from error

    try:
        payment = Payment.find_one(payment_id)  # проверяем статус платежа
    except RequestException as error:
        logger.error(
            msg={f"Yookassa payment status check failed for {payment_id}": error}
        )
        raise YookassaPaymentStatusCheckError(payment_id, error) from error

    if payment.status != "succeeded":
        logger.error(
            f"Yookassa error: Payment {payment_id} failed to finalize as 'succeeded'."
        )
        raise YookassaPaymentFinalizeError(payment_id)

    else:
        update_payment_info(payment_id=payment_id, application=application)


@atomic
def update_payment_info(payment_id: uuid, application: Application) -> None:
    """Обновление информации о платеже"""

    Application.objects.filter(payment_id=payment_id).update(
        status=Application.COMPLETED
    )
    ApplicationLog.objects.create(
        application=application,
        status=Application.COMPLETED
    )
    Account.objects.filter(number=application.account.number).update(
        balance=F("balance") + application.amount
    )
