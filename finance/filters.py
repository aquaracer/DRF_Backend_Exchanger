from typing import Any

from django_filters import rest_framework as df_filters
from django_filters.fields import CSVWidget, MultipleChoiceField

from .models import Account, Transaction


class MultipleField(MultipleChoiceField):
    def valid_value(self, value: Any) -> bool:
        return True


class MultipleFilter(df_filters.MultipleChoiceFilter):
    field_class = MultipleField


class TranscationFilter(df_filters.FilterSet):
    """Фильтр транзакций"""

    currency = MultipleFilter(
        field_name="currency__short_name", lookup_expr="exact", widget=CSVWidget
    )
    start_date = df_filters.DateTimeFilter(field_name="created", lookup_expr="gte")
    end_date = df_filters.DateTimeFilter(field_name="created", lookup_expr="lte")
    min_amount = df_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = df_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = (
            "transaction_type",
            "currency",
            "start_date",
            "end_date",
            "created",
            "amount",
            "min_amount",
            "max_amount",
        )


class AccountFilter(df_filters.FilterSet):
    """Фильтр списка счетов"""

    currency = MultipleFilter(
        field_name="currency__short_name", lookup_expr="exact", widget=CSVWidget
    )
    balance_from = df_filters.NumberFilter(field_name="balance", lookup_expr="gte")
    balance_up_to = df_filters.NumberFilter(field_name="balance", lookup_expr="lte")
    username = df_filters.NumberFilter(field_name="user__username", lookup_expr="lte")

    class Meta:
        model = Account
        fields = ("currency", "number", "balance", "balance_from", "balance_up_to")
