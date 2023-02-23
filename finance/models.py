import uuid
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import AbstarctBaseModel, User


class Currency(AbstarctBaseModel):
    """Валюта"""

    symbol = models.CharField(verbose_name='Символ валюты', max_length=2)
    code = models.CharField(verbose_name='Код валюты', validators=[MinLengthValidator(3), RegexValidator("^[0-9]+$")],
                            max_length=3)
    short_name = models.CharField(verbose_name='Краткое название', max_length=3)
    full_name = models.CharField(verbose_name='Полное название', max_length=50)

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'

    def __str__(self):
        return f'{self.id} | {self.full_name} '


class Account(AbstarctBaseModel):
    """Счет"""

    # Отношения
    user = models.ForeignKey('users.User', verbose_name='Пользователь', on_delete=models.SET_NULL, null=True)
    сurrency = models.ForeignKey(Currency, verbose_name='Валюта', on_delete=models.SET_NULL, null=True)

    # Поля
    number = models.UUIDField(verbose_name='Номер счета', default=uuid.uuid4)
    balance = models.DecimalField(verbose_name='Баланс', max_digits=11, decimal_places=2, default=0,
                                  validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'

    def __str__(self):
        return f'{self.id} | {self.number} | {self.balance} | {self.сurrency.symbol}'


class Transaction(AbstarctBaseModel):
    """Транзакция"""

    DEBIT = 'debit'
    CREDIT = 'credit'

    TYPE = (
        (DEBIT, 'Списание'),
        (CREDIT, 'Пополнение'),
    )

    # Отношения
    sender_account = models.ForeignKey(Account, verbose_name='Счет отправителя', on_delete=models.SET_NULL, null=True,
                                       related_name='sender_account')
    reciever_account = models.ForeignKey(Account, verbose_name='Счет получателя', on_delete=models.SET_NULL, null=True,
                                         related_name='receiver_account')
    currency = models.ForeignKey(Currency, verbose_name='Валюта', on_delete=models.SET_NULL, null=True)

    # Поля
    description = models.CharField(verbose_name='Назначение платежа', max_length=300)
    amount = models.DecimalField(verbose_name='Сумма', max_digits=11, decimal_places=2, default=0,
                                 validators=[MinValueValidator(0)])
    transaction_type = models.CharField(verbose_name='Тип платежа', choices=TYPE, max_length=20)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f'{self.id} | {self.created} | {self.amount} | {self.currency.symbol} | {self.transaction_type} | ' \
               f'отправитель {self.sender_account.number} | получатель {self.reciever_account.number}'


@receiver(post_save, sender=User)
def create_accounts(sender, instance, created, *args, **kwargs):
    """
    Сигнал, срабатывающий при создании учетной записи пользователя.
    Создает счета основных валют и привязывает их к созданной учетной записи пользователя.
    """

    if created:
        ids = Currency.objects.all().values_list('id', flat=True)
        account_batch = []
        for id in ids:
            account_batch.append(Account(user=instance, сurrency_id=id))

        Account.objects.bulk_create(account_batch)
