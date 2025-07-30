from django.contrib import admin

from .models import Account, Application, Currency, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "account",
        "currency",
        "payment_id",
        "amount",
        "payment_type",
        "status",
        "error",
    )
    readonly_fields = ("payment_id",)
