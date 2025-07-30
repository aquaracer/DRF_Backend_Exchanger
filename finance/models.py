import uuid

from django.core.validators import MinLengthValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import AbstarctBaseModel


class Currency(AbstarctBaseModel):
    """Валюта"""

    symbol = models.CharField(verbose_name=_("Символ валюты"), max_length=2)
    code = models.CharField(
        verbose_name=_("Код валюты"),
        validators=[MinLengthValidator(3), RegexValidator("^[0-9]+$")],
        max_length=3,
    )
    short_name = models.CharField(verbose_name=_("Краткое название"), max_length=3)
    full_name = models.CharField(verbose_name=_("Полное название"), max_length=50)

    class Meta:
        verbose_name = _("Валюта")
        verbose_name_plural = _("Валюты")

    def __str__(self) -> str:
        return f"{self.id} | {self.full_name}"


class Account(AbstarctBaseModel):
    """Счет"""

    user = models.ForeignKey(
        "users.User",
        verbose_name=_("Пользователь"),
        on_delete=models.SET_NULL,
        null=True,
    )
    сurrency = models.ForeignKey(
        Currency, verbose_name=_("Валюта"), on_delete=models.SET_NULL, null=True
    )

    number = models.UUIDField(verbose_name=_("Номер счета"), default=uuid.uuid4)
    balance = models.DecimalField(
        verbose_name=_("Баланс"),
        max_digits=11,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = _("Счет")
        verbose_name_plural = _("Счета")

    def __str__(self) -> str:
        return f"{self.id} | {self.number} | {self.balance} | {self.сurrency.symbol}"


class Transaction(AbstarctBaseModel):
    """Транзакция"""

    DEBIT = "debit"
    CREDIT = "credit"

    TYPE = (
        (DEBIT, _("Списание")),
        (CREDIT, _("Пополнение")),
    )

    sender_account = models.ForeignKey(
        Account,
        verbose_name=_("Счет отправителя"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="sender_account",
    )
    reciever_account = models.ForeignKey(
        Account,
        verbose_name=_("Счет получателя"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="receiver_account",
    )
    currency = models.ForeignKey(
        Currency, verbose_name=_("Валюта"), on_delete=models.SET_NULL, null=True
    )

    description = models.CharField(verbose_name=_("Назначение платежа"), max_length=300)
    amount = models.DecimalField(
        verbose_name=_("Сумма"),
        max_digits=11,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    transaction_type = models.CharField(
        verbose_name=_("Тип платежа"), choices=TYPE, max_length=20
    )

    class Meta:
        verbose_name = _("Транзакция")
        verbose_name_plural = _("Транзакции")

    def __str__(self) -> str:
        return (
            f"{self.id} | sender account: {self.sender_account} | receiver "
            f"account: {self.reciever_account} | currency {self.currency} | "
            f"descrition: {self.description}| amount: {self.amount} |"
            f" transaction type: {self.transaction_type}"
        )


class Application(AbstarctBaseModel):
    """Заявка на ввод/вывод средств"""

    REFILL = "refill"
    WITHDRAWAL = "withdrawal"

    PAYMENT_TYPE = (
        (REFILL, _("Ввод")),
        (WITHDRAWAL, _("Вывод")),
    )

    PENDING = "pending"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ERROR = "error"

    STATUS = (
        (PENDING, _("В обработке")),
        (WAITING_FOR_CAPTURE, _("К зачислению")),
        (CANCELLED, _("Отменено")),
        (COMPLETED, _("Выполнено")),
        (ERROR, _("Ошибка")),
    )

    account = models.ForeignKey(
        Account, verbose_name=_("Счет"), on_delete=models.SET_NULL, null=True
    )
    currency = models.ForeignKey(
        Currency, verbose_name=_("Валюта"), on_delete=models.SET_NULL, null=True
    )
    payment_id = models.UUIDField(
        verbose_name=_("Id платежа"), unique=True, editable=False, blank=True, null=True
    )
    amount = models.DecimalField(
        verbose_name=_("Сумма"),
        max_digits=11,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    payment_type = models.CharField(
        verbose_name=_("Тип платежа"), choices=PAYMENT_TYPE, max_length=20
    )
    status = models.CharField(verbose_name=_("Статус"), choices=STATUS, max_length=20)
    error = models.CharField(
        verbose_name=_("Ошибка"), max_length=3000, blank=True, null=True
    )

    class Meta:
        verbose_name = _("Заявка")
        verbose_name_plural = _("Заявка")

    def __str__(self) -> str:
        return (
            f"{self.id} | account: {self.amount} | currency: {self.currency} | "
            f"payment_id: {self.payment_id} | amount: {self.amount} | "
            f"payment_type: {self.payment_type} |"
            f" status: {self.status} | error: {self.error}"
        )


class ApplicationLog(AbstarctBaseModel):
    """История изменений заявки"""

    application = models.ForeignKey(
        Application, verbose_name=_("Заявка"), on_delete=models.SET_NULL, null=True
    )
    status = models.CharField(
        verbose_name=_("Статус"), choices=Application.STATUS, max_length=20
    )

    def __str__(self) -> str:
        return (
            f"{self.id} | application_id: {self.application.id} | created_at:"
            f" {self.created} | updated_at: {self.last_updated} | status: "
            f"{self.status}"
        )
