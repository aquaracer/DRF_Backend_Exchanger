from django.db.models import F
from rest_framework.exceptions import ValidationError
import redis, os

from .models import Account, Transaction
from .tasks import send_notification


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
