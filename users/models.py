from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.auth.models import AbstractUser

from common.models import AbstarctBaseModel


class User(AbstractUser):
    """Пользователь"""

    USER = 'user'
    ADMIN = 'admin'

    TYPE = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.EmailField(verbose_name='Логин', max_length=255, unique=True)
    middle_name = models.CharField(verbose_name='Отчество', max_length=150, blank=True, null=True)
    type = models.CharField(verbose_name='Тип аккаунта', choices=TYPE, max_length=20, default=USER)
    phone = models.CharField(
        verbose_name='Телефон',
        max_length=16,
        validators=[
            MinLengthValidator(12),
            RegexValidator(
                regex=r'^\+?1?\d{11}$',
                message='Телефон должен быть в формате: +7999999999'
            )
        ],
        unique=True,
        blank=True,
        null=True
    )
    sms_notification = models.BooleanField(verbose_name='Уведомление по смс', default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.id} | {self.first_name} | {self.last_name} |' f' {self.username}'


class UserAdditionalInfo(AbstarctBaseModel):
    """Дополнительная информация о пользователе"""

    M = "Муж"
    W = "Жен"

    SEX = (
        (M, "Мужской"),
        (W, "Женский")
    )

    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE, default='',
                                null=True, blank=True)

    date_of_birth = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    sex = models.CharField(verbose_name='Пол', choices=SEX, max_length=30, default=M, blank=True)
    passport_photo_reversal = models.ImageField(verbose_name='Фото разворота паспорта',
                                                upload_to='passport_photo_reversal', blank=True)
    passport_photo_registered_address = models.ImageField(verbose_name='Фото страницы с пропиской',
                                                          upload_to='passport_photo_reversal', blank=True)
    registered_address = models.CharField(verbose_name='Прописка', max_length=250, null=True, blank=True)
    passport_series = models.CharField(verbose_name='Серия паспорта',
                                       validators=[MinLengthValidator(4), RegexValidator("^[0-9]+$")],
                                       max_length=4, null=True, blank=True)
    passport_number = models.CharField(verbose_name='Номер паспорта',
                                       validators=[MinLengthValidator(6), RegexValidator("^[0-9]+$")], max_length=6,
                                       default='')
    subdivision_code = models.CharField(verbose_name='Код подразделения', validators=[MinLengthValidator(7)],
                                        max_length=7, default='')
    date_of_issue = models.DateField(verbose_name='Дата выдачи паспорта', null=True, blank=True)

    class Meta:
        verbose_name = 'Дополнительная информация о пользователе'
        verbose_name_plural = 'Дополнительная информация о пользователе'

    def __str__(self):
        if self.user:
            return f'{self.id} | {self.user.first_name} | {self.user.last_name} |' f' {self.user.username}'
