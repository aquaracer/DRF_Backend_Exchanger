import uuid
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator, MinValueValidator

from users.models import AbstarctBaseModel


class Currency(AbstarctBaseModel):
    """Валюта"""

    symbol = models.CharField(verbose_name='Символ валюты', max_length=2)
    code = models.CharField(
        verbose_name='Код валюты',
        validators=[MinLengthValidator(3), RegexValidator("^[0-9]+$")],
        max_length=3,
    )
    short_name = models.CharField(verbose_name='Краткое название', max_length=3)
    full_name = models.CharField(verbose_name='Полное название', max_length=50)

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'

    def __str__(self):
        return f'{self.id} | {self.full_name} '


class Account(AbstarctBaseModel):
    """Счет"""

    user = models.ForeignKey('users.User', verbose_name='Пользователь', on_delete=models.SET_NULL, null=True)
    currency = models.ForeignKey(Currency, verbose_name='Валюта', on_delete=models.SET_NULL, null=True)

    number = models.UUIDField(verbose_name='Номер счета', default=uuid.uuid4)
    balance = models.DecimalField(
        verbose_name='Баланс',
        max_digits=11,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

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

    sender_account = models.ForeignKey(
        Account,
        verbose_name='Счет отправителя',
        on_delete=models.SET_NULL, null=True,
        related_name='sender_account',
    )
    reciever_account = models.ForeignKey(
        Account,
        verbose_name='Счет получателя',
        on_delete=models.SET_NULL,
        null=True,
        related_name='receiver_account',
    )
    currency = models.ForeignKey(Currency, verbose_name='Валюта', on_delete=models.SET_NULL, null=True)

    description = models.CharField(verbose_name='Назначение платежа', max_length=300)
    amount = models.DecimalField(
        verbose_name='Сумма',
        max_digits=11,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    transaction_type = models.CharField(verbose_name='Тип платежа', choices=TYPE, max_length=20)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f'{self.id}'


class Application(AbstarctBaseModel):
    """Заявка на ввод/вывод средств"""

    REFILL = 'refill'
    WITHDRAWAL = 'withdrawal'

    TYPE = (
        (REFILL, 'Ввод'),
        (WITHDRAWAL, 'Вывод'),
    )

    PENDING = 'pending'
    WAITING_FOR_CAPTURE = 'waiting_for_capture'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    ERROR = 'error'

    STATUS = (
        (PENDING, 'В обработке'),
        (WAITING_FOR_CAPTURE, 'К зачислению'),
        (CANCELLED, 'Отменено'),
        (COMPLETED, 'Выполнено'),
        (ERROR, 'Ошибка'),
    )

    account = models.ForeignKey(Account, verbose_name='Счет', on_delete=models.SET_NULL, null=True)
    currency = models.ForeignKey(Currency, verbose_name='Валюта', on_delete=models.SET_NULL, null=True)

    payment_id = models.UUIDField(verbose_name="Id платежа", unique=True, editable=False, blank=True, null=True)
    amount = models.DecimalField(
        verbose_name='Сумма',
        max_digits=11,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    type = models.CharField(verbose_name='Тип платежа', choices=TYPE, max_length=20)
    status = models.CharField(verbose_name='Статус', choices=STATUS, max_length=20)
    error = models.CharField(verbose_name='Ошибка', max_length=3000, blank=True, null=True)


class ApplicationLog(AbstarctBaseModel):
    """История изменений заявки"""

    application = models.ForeignKey(Application, verbose_name='Заявка', on_delete=models.SET_NULL, null=True)

    status = models.CharField(verbose_name='Статус', choices=Application.STATUS, max_length=20)
