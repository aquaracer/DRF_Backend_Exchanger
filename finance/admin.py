from django.contrib import admin

from .models import Account, Currency, Transaction, Application


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
    list_display = ('account',  'currency', 'payment_id', 'amount', 'type', 'status' , 'error' )
    readonly_fields = ('payment_id',)


