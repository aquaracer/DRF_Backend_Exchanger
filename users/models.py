from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import AbstarctBaseModel


class User(AbstractUser, AbstarctBaseModel):
    """Пользователь"""

    USER = "user"
    ADMIN = "admins"

    TYPE = (
        (USER, _("Обычный пользователь")),
        (ADMIN, _("Администратор")),
    )

    username = models.EmailField(
        verbose_name=_("Логин"),
        max_length=255,
        unique=True,
        help_text=_("Обязательное поле. Должно быть действительным email адресом."),
    )

    middle_name = models.CharField(
        verbose_name=_("Отчество"), max_length=150, blank=True, null=True
    )

    type = models.CharField(
        verbose_name=_("Тип аккаунта"), choices=TYPE, max_length=20, default=USER
    )

    phone = models.CharField(
        verbose_name=_("Номер телефона"),
        max_length=16,
        validators=[
            MinLengthValidator(12),
            RegexValidator(
                regex=r"^\+?1?\d{11}$",
                message=_("Номер телефона должен быть в формате: +79999999999"),
            ),
        ],
        unique=True,
        blank=True,
        null=True,
        help_text=_("Номер телефона в международном формате"),
    )

    sms_notification = models.BooleanField(
        verbose_name=_("SMS уведомления"),
        default=False,
        help_text=_("Включить/выключить SMS уведомления"),
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.id} | {self.get_full_name()} | {self.username}"

    def get_full_name(self) -> str:
        """Возвращает полное имя пользователя."""
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(filter(None, parts))


class UserAdditionalInfo(AbstarctBaseModel):
    """Дополнительная информация о пользователе."""

    MALE = "Муж"
    FEMALE = "Жен"

    GENDER_CHOICES = (
        (MALE, _("Муж")),
        (FEMALE, _("Жен"))
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="additional_info"
    )

    date_of_birth = models.DateField(
        verbose_name=_("Дата рождения"), null=True, blank=True
    )

    gender = models.CharField(
        verbose_name=_("Пол"),
        choices=GENDER_CHOICES,
        max_length=30,
        default=MALE,
        blank=True,
    )

    passport_photo_reversal = models.ImageField(
        verbose_name=_("Фото главной страницы паспорта"),
        upload_to="passport_photos/%Y/%m/%d/",
        blank=True,
        help_text=_("Фото главной страницы паспорта"),
    )

    passport_photo_registered_address = models.ImageField(
        verbose_name=_("Фото страницы паспорта с адресом регистрации"),
        upload_to="passport_photos/%Y/%m/%d/",
        blank=True,
        help_text=_("Фото страницы паспорта с адресом регистрации"),
    )

    registered_address = models.CharField(
        verbose_name=_("Адрес регистрации"), max_length=250, null=True, blank=True
    )

    passport_series = models.CharField(
        verbose_name=_("Серия паспорта"),
        validators=[
            MinLengthValidator(4),
            RegexValidator(
                "^[0-9]+$", _("Серия паспорта должна содержать только цифры")
            ),
        ],
        max_length=4,
        null=True,
        blank=True,
    )

    passport_number = models.CharField(
        verbose_name=_("Номер паспорта"),
        validators=[
            MinLengthValidator(6),
            RegexValidator(
                "^[0-9]+$", _("Номер паспорта должен содержать только цифры")
            ),
        ],
        max_length=6,
        null=True,
        blank=True,
    )

    subdivision_code = models.CharField(
        verbose_name=_("Код подразделения"),
        validators=[MinLengthValidator(7)],
        max_length=7,
        null=True,
        blank=True,
    )

    date_of_issue = models.DateField(
        verbose_name=_("Дата выдачи паспорта"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Дополнительная информация")
        verbose_name_plural = _("Дополнительная информация")
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.id} | {self.user.get_full_name()} | {self.user.username}"
