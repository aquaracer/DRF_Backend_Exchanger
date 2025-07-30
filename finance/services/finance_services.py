import logging
import os
from decimal import Decimal
from typing import Any

import redis
from django.db.models import F
from django.db.transaction import atomic

from config import settings

from ..models import Account, Transaction
from ..tasks import send_sms_notification_task

logger = logging.getLogger("__name__")


def calculate_new_amounts(
        debit_currency: str, credit_currency: str, debit_amount: Decimal
) -> Decimal:
    """Рассчет суммы к зачислению при переводе средств"""

    redis_instance = redis.StrictRedis(
        host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"), db=0
    )

    if credit_currency == "RUR":
        new_amount = debit_amount * redis_instance.get(debit_currency)
    elif debit_currency == "RUR":
        new_amount = debit_amount * round(1 / redis_instance.get(debit_currency), 4)
    elif debit_currency == "RUR":
        new_amount = debit_amount
    else:
        new_amount = debit_amount * redis_instance.get(debit_currency)
        new_amount = round(
            new_amount * round(1 / redis_instance.get(debit_currency), 4), 2
        )
    return new_amount


def send_funds(transfer_data: dict) -> None:
    """Перевод средств (на свой аккаунт или аккаунт другого пользователя)"""

    senders_account, receivers_account = update_account_balances(
        transfer_data=transfer_data
    )
    send_sms_notification(
        transfer_data=transfer_data,
        senders_account=senders_account,
        receivers_account=receivers_account
    )


@atomic
def update_account_balances(transfer_data: dict) -> tuple[Account, Account]:
    """
    Обновление балансов счетов при переводе и добавление записей в историю транзакций
    """

    Account.objects.filter(
        number=transfer_data.get("senders_account_number")).update(
        balance=F("balance") - transfer_data.get("amount_to_send")
    )
    Account.objects.filter(transfer_data.get("receivers_account_number")).update(
        balance=F("balance") + transfer_data.get("amount_to_receive")
    )

    if transfer_data.get("receiver_type") == "self":
        debit_description = "перевод средств между своими счетами"
        credit_description = "перевод средств между своими счетами"
    else:
        debit_description = "перевод средств другому пользователю"
        credit_description = "зачисление средств от другого пользователя"

    senders_account = Account.objects.get(
        number=transfer_data.get("senders_account_number")
    )
    receivers_account = Account.objects.get(
        number=transfer_data.get("receivers_account_number")
    )

    batch = [
        Transaction(
            sender_account=senders_account,
            reciever_account=receivers_account,
            description=debit_description,
            amount=transfer_data.get("amount_to_send"),
            transaction_type=Transaction.DEBIT
        ),
        Transaction(
            sender_account=senders_account,
            reciever_account=receivers_account,
            description=credit_description,
            amount=transfer_data.get("amount_to_send"),
            transaction_type=Transaction.CREDIT
        ),
    ]
    Transaction.objects.bulk_create(batch)

    return senders_account, receivers_account


def send_sms_notification(
        transfer_data: dict,
        receivers_account: Account,
        senders_account: Account
) -> None:
    """Отправка в фоновом режиме смс-уведомления о переводе получателю платежа"""

    if transfer_data.get("receiver_type") == "counterparty" and \
            receivers_account.user.sms_notification \
            and receivers_account.user.phone:
        message = (
            f"Зачислен перевод на сумму {transfer_data.get('amount_to_receive')}"
            f"{transfer_data.get('currency_to_receive')} от "
            f"{senders_account.user.first_name}{senders_account.user.last_name}"
        )
    sms_sender_url = (
        f"{settings.SMS_PROVIDER_URL}{settings.SMS_PROVIDER_LOGIN}&psw="
        f"{settings.SMS_PROVIDER_PASSWORD}&phones="
        f"{receivers_account.user.phone}&mes={message}"
    )

    send_sms_notification_task.delay(sms_sender_url=sms_sender_url)


def get_exchange_rates() -> dict[str, Any]:
    """Получение курсов валют из Redis"""

    redis_storage = redis.StrictRedis(
        host=os.environ.get("REDIS_HOST"),
        port=os.environ.get("REDIS_PORT"),
        db=0
    )
    rates: dict[str, Any] = {}
    for currency in ["USD", "EUR", "CNY"]:
        rates[currency] = redis_storage.get(currency)
    return rates




