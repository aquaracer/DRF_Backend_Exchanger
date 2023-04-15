from django_filters.fields import CSVWidget, MultipleChoiceField
from django_filters import rest_framework as df_filters

from .models import Transaction, Account


class MultipleField(MultipleChoiceField):
    def valid_value(self, value):
        return True


class MultipleFilter(df_filters.MultipleChoiceFilter):
    field_class = MultipleField


class TranscationFilter(df_filters.FilterSet):
    """Фильтр транзакций"""

    currency = MultipleFilter(field_name='currency__short_name', lookup_expr='exact',
                              widget=CSVWidget)  # мультиселект фильтр по типу валюты
    start_date = df_filters.DateTimeFilter(field_name='created',
                                           lookup_expr='gte')  # фильтр по начальной дате диапазона дат
    end_date = df_filters.DateTimeFilter(field_name='created',
                                         lookup_expr='lte')  # фильтр по конечно дате диапазона дат
    min_amount = df_filters.NumberFilter(field_name='amount',
                                         lookup_expr='gte')  # фильтр  по сумме транзакции >= заданного числа
    max_amount = df_filters.NumberFilter(field_name='amount',
                                         lookup_expr='lte')  # фильтр  по сумме транзакции <= заданного числа

    class Meta:
        model = Transaction
        fields = (
            'transaction_type', 'currency', 'start_date', 'end_date', 'created', 'amount', 'min_amount', 'max_amount'
        )


class AccountFilter(df_filters.FilterSet):
    """Фильтр списка счетов"""

    currency = MultipleFilter(field_name='currency__short_name', lookup_expr='exact', widget=CSVWidget)
    balance_from = df_filters.NumberFilter(field_name='balance', lookup_expr='gte')
    balance_up_to = df_filters.NumberFilter(field_name='balance', lookup_expr='lte')
    username = df_filters.NumberFilter(field_name='user__username', lookup_expr='lte')

    class Meta:
        model = Account
        fields = ('currency', 'number', 'balance', 'balance_from', 'balance_up_to')
