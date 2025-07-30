from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Account, Application, Transaction


class AccountSerializer(serializers.ModelSerializer):
    """Счет"""

    class Meta:
        model = Account
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    """Транзакция"""

    class Meta:
        model = Transaction
        fields = "__all__"


class CreateTransactionSerializer(serializers.Serializer):
    """Совершение перевода"""

    senders_account_number = serializers.UUIDField(required=True)
    amount_to_send = serializers.DecimalField(
        required=True,
        min_value=0.01,
        max_digits=11,
        decimal_places=2
    )
    receivers_account_number = serializers.UUIDField(required=True)
    amount_to_receive = serializers.DecimalField(
        required=True,
        min_value=0.01,
        max_digits=11,
        decimal_places=2
    )
    receiver_type = serializers.ChoiceField(
        choices=["self", "counterparty"],
        required=True
    )

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        user = self.context['request_user']

        if not Account.objects.filter(
                user=user,
                number=data["senders_account_number"]
        ).exists():
            raise ValidationError(
                """Счет списания средств не принадлежит данному пользователю. 
                Проверьте правильность счета и повторите попытку"""
            )

        if data.get("receiver_type") == "self":
            if not Account.objects.filter(
                    user=user,
                    number=data["receivers_account_number"]
            ).exists():
                raise ValidationError(
                    """Счет для получения средств не принадлежит данному пользователю.
                     Проверьте правильность счета и повторите попытку"""
                )
        else:
            if not Account.objects.filter(
                    number=data["receivers_account_number"]
            ).exists():
                raise ValidationError(
                    "Счет для получения средств не найден в системе. "
                    "Проверьте правильность счета и повторите попытку"
                )

        if not Account.objects.filter(
                number=data["senders_account_number"],
                balance__gte=data['amount_to_send']
        ).exists():
            raise ValidationError("На счете недостаточно средств")

        return data


class CalculateAmountsSerializer(serializers.Serializer):
    """Рассчет суммы к зачислению"""

    debit_account = serializers.UUIDField(required=True)
    debit_currency = serializers.ChoiceField(choices=["RUR", "USD", "EUR", "CNY"])
    credit_currency = serializers.ChoiceField(choices=["RUR", "USD", "EUR", "CNY"])
    debit_amount = serializers.DecimalField(
        required=True, min_value=0.01, max_digits=11, decimal_places=2
    )

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if not Account.objects.filter(
                number=data.get("debit_account"),
                balance__gte=data.get("debit_amount")
        ).existst():
            raise ValidationError(
                "На счете недостаточно средств для выполнения операции"
            )
        return data


class UpdateBalanceSerializer(serializers.ModelSerializer):
    """Изменить баланс пользователя через личный кабинет Администратора"""

    class Meta:
        model = Account
        fields = ("balance",)


class CreateApplicationSerializer(serializers.ModelSerializer):
    """Создание заявки на вывод средств"""

    class Meta:
        model = Application
        fields = ("amount", "payment_type", "currency")


class ApplicationSerializer(serializers.ModelSerializer):
    """Заявка на вывод средств"""

    class Meta:
        model = Application
        fields = "__all__"
