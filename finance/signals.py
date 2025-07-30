from typing import Any

from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver

from finance.models import Account, Currency
from users.models import User


@receiver(post_save, sender=User)
def create_accounts(
        sender: Model, instance: User, created: bool, *args: Any, **kwargs: Any
) -> None:
    """
    Сигнал, срабатывающий при создании учетной записи пользователя.
    Создает счета основных валют и привязывает их к созданной учетной записи
    пользователя.
    """

    if created:
        currency_ids = Currency.objects.all().values_list("id", flat=True)
        accounts_batch: list[Account] = [
            Account(user=instance, currency_id=currency_id)
            for currency_id in currency_ids
        ]
        Account.objects.bulk_create(accounts_batch)
