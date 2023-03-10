from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Account, Transaction, Application


class AccountSerializer(serializers.ModelSerializer):
    """Счет"""

    username = serializers.CharField(source='user.username')

    class Meta:
        model = Account
        fields = '__all__'


class TransactionSerializer(serializers.Serializer):
    """Транзакция"""

    class Meta:
        model = Transaction
        fields = '__all__'


class YourselfTransactionSerializer(serializers.Serializer):
    """Перевод себе"""

    senders_account = serializers.UUIDField(required=True)
    amount_to_send = serializers.DecimalField(required=True, min_value=0.01, max_digits=11, decimal_places=2)
    receivers_account = serializers.UUIDField(required=True)
    amount_to_receive = serializers.DecimalField(required=True, min_value=0.01, max_digits=11, decimal_places=2)
    receiver_type = serializers.ChoiceField(choices=['self', 'counterparty'], required=True)


class CalculateAmountsSerializer(serializers.Serializer):
    """Рассчет суммы к зачислению"""

    debit_account = serializers.UUIDField(required=True)
    debit_currency = serializers.ChoiceField(choices=['RUR', 'USD', 'EUR', 'CNY'])
    credit_currency = serializers.ChoiceField(choices=['RUR', 'USD', 'EUR', 'CNY'])
    debit_amount = serializers.DecimalField(required=True, min_value=0.01, max_digits=11, decimal_places=2)

    def validate(self, data):
        if not Account.objects.filter(number=data.get('debit_account'),
                                      balance__gte=data.get('debit_amount')).existst():
            raise ValidationError('На счете недостаточно средств для выполнения операции')


class UpdateBalanceSerializer(serializers.ModelSerializer):
    """Изменить баланс пользователя через личный кабинет Администратора"""

    class Meta:
        model = Account
        fields = ('balance',)

class CreateApplicationSerializer(serializers.ModelSerializer):
    """Создание заявки на вывод средств"""

    class Meta:
        model = Application
        fields = ('amount', 'type')

class ApplicationSerializer(serializers.ModelSerializer):
    """Заявка на вывод средств"""

    class Meta:
        model = Application
        fields = '__all__'