from django.db.models.signals import post_save
from django.dispatch import receiver

from finance.models import Currency, Account
from users.models import User

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
