from django.db.models import F
from rest_framework.exceptions import ValidationError
import redis, os, uuid, json, requests, logging
from yookassa import Payment, Configuration
from yookassa.domain.notification import WebhookNotification
from requests import RequestException

from .models import Account, Transaction, Currency, Application, ApplicationLog
from .tasks import send_notification
from common.exceptions import BadRequest

logger = logging.getLogger('__name__')


def calculate_new_amounts(debit_currency, credit_currency, debit_amount):
    """Рассчет суммы к зачислению при переводе средств"""

    redis_instance = redis.StrictRedis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)

    if credit_currency == "RUR":
        new_amount = debit_amount * redis_instance.get(debit_currency)
    elif debit_currency == "RUR":
        new_amount = debit_amount * round(1 / redis_instance.get(debit_currency), 4)
    elif debit_currency == "RUR":
        new_amount = debit_amount
    else:
        new_amount = debit_amount * redis_instance.get(debit_currency)
        new_amount = round(new_amount * round(1 / redis_instance.get(debit_currency), 4), 2)

    return new_amount


def send_funds(serializer, request):
    """Перевод средств (на свой аккаунт или аккаунт другого пользователя)"""

    senders_account = serializer.validated_data.get('senders_account')
    amount_to_send = serializer.validated_data.get('amount_to_send')
    receivers_account = serializer.validated_data.get('receivers_account')
    amount_to_receive = serializer.validated_data.get('amount_to_receive')
    currency_to_receive = serializer.validated_data.get('currency_to_receive')
    receiver_type = serializer.validated_data.get('receiver_type')

    if not Account.objects.filter(user=request.user, number=senders_account).exists():
        raise ValidationError(
            'Счет списания средств не принадлежит данному пользователю. Проверьте правильность счета и повторите попытку'
        )

    if receiver_type == 'self':
        if not Account.objects.filter(user=request.user, number=receivers_account).exists():
            raise ValidationError(
                'Счет для получения средств не принадлежит данному пользователю.'
                ' Проверьте правильность счета и повторите попытку'
            )
    else:
        if not Account.objects.filter(number=receivers_account).exists():
            raise ValidationError(
                'Счет для получения средств не найден в системе. Проверьте правильность счета и повторите попытку'
            )

    if not Account.objects.filter(number=senders_account, balance__gte=amount_to_send).exists():
        raise ValidationError('На счете недостаточно средств')

    Account.select_for_update().filter(number=senders_account).update(balance=F('balance') - amount_to_send)
    Account.select_for_update().filter(number=receivers_account).update(balance=F('balance') - amount_to_receive)

    if receiver_type == 'self':
        debit_description = 'перевод средств между своими счетами'
        credit_description = 'перевод средств между своими счетами'
    else:
        debit_description = 'перевод средств другому пользователю'
        credit_description = 'зачисление средств от другого пользователя'

    batch = [
        Transaction(
            sender_account=senders_account,
            reciever_account=receivers_account,
            description=debit_description,
            amount=amount_to_send,
            transaction_type=Transaction.DEBIT
        ),
        Transaction(
            sender_account=senders_account,
            reciever_account=receivers_account,
            description=credit_description,
            amount=amount_to_send,
            transaction_type=Transaction.CREDIT
        ),
    ]
    Transaction.objects.bulk_create(batch)

    if receiver_type == 'counterparty':
        send_notification.delay(senders_account, receivers_account, currency_to_receive)


def create_application(serializer, request):
    """Создание завяки на ввод средств"""

    Configuration.account_id = os.environ.get('YOOKASSA_ACCOUNT_ID')
    Configuration.secret_key = os.environ.get('YOOKASSA_SECRET_KEY')

    currency = Currency.objects.get(short_name='RUR')
    account_id = Account.objects.filter(сurrency_id=currency.id, user=request.user).values_list('id', flat=True)[0]
    application = serializer.save(currency=currency, status=Application.PENDING, account_id=account_id)

    try:
        payment = Payment.create({
            "amount": {
                "value": str(serializer.validated_data.get('amount')),
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://www.example.com/return_url"
            },
            "description": f"Заявка на поплнение счета {application.id}"
        }, str(uuid.uuid4()))
    except RequestException as error:
        logger.error(msg={'Ошибка на стороне Yookassa при создании платежа': error})
        raise BadRequest('Ошибка на стороне Yookassa при создании платежа', error)

    data = {'confirmation_url': payment.confirmation.confirmation_url}

    application.payment_id = payment.payment_method.id
    application.save()

    return data


def to_handle_webhook(request):
    """Обработка вебхука"""

    Configuration.account_id = os.environ.get('YOOKASSA_ACCOUNT_ID')
    Configuration.secret_key = os.environ.get('YOOKASSA_SECRET_KEY')
    event_json = json.loads(request.body)

    try:
        notification_object = WebhookNotification(event_json)
    except Exception as error:
        logger.error(msg={'Не удалось получить данный из джейсон при обработке webhook от Yookassa': error})
        raise BadRequest('Не удалось получить данный из джейсон при обработке webhook от Yookassa', error)


    payment_id = notification_object.object.id

    if not Application.objects.filter(payment_id=payment_id, status=Application.PENDING).exists():
        return

    application = Application.objects.get(payment_id=payment_id)

    try:
        Payment.capture(
            payment_id,
            {
                "amount": {
                    "value": str(application.amount),
                    "currency": "RUB"
                }
            },
            str(uuid.uuid4())
        )
    except RequestException as error:
        logger.error(msg={f'Ошибка на стороне Yookassa при подтверждении платежа {payment_id}': error})
        raise BadRequest(f'Ошибка на стороне Yookassa при подтверждении платежа {payment_id}', error)

    try:
        payment = Payment.find_one(payment_id)
    except RequestException as error:
        logger.error(msg={f'Ошибка на стороне Yookassa при проверка статуса платежа {payment_id}': error})
        raise BadRequest(f'Ошибка на стороне Yookassa при проверка статуса платежа {payment_id}', error)

    if payment.status == 'succeeded':
        Application.objects.filter(payment_id=payment_id).update(status=Application.COMPLETED)
        ApplicationLog.objects.create(application=application, status=Application.COMPLETED)
        Account.objects.filter(number=application.account.number).update(balance=F('balance') + application.amount)

    else:
        raise BadRequest(f'Ошибка на стороне Yookassa. Платежа {payment_id} не переведен в статус succeeded', None)

    data = {'payment': payment}
    return data


