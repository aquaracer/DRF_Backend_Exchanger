from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from finance.filters import AccountFilter, TranscationFilter
from finance.models import Account, Transaction
from finance.pagination import AccountPagination, TranscationPagination
from finance.serializers import (
    AccountSerializer,
    TransactionSerializer,
    UpdateBalanceSerializer,
)


@extend_schema(tags=["Admins (ЛК Администратора)"])
@extend_schema_view(
    list=extend_schema(
        summary="Список счетов пользователя в ЛК администратора",
    ),
    partial_update=extend_schema(
        summary="Изменение баланса пользователя в ЛК администратора",
        request=UpdateBalanceSerializer,
    ),
)
class AdminAccountsViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin):
    """
    Счета пользователей в ЛК Администратора
    методы:
    partial_update - изменение баланса счета
    list - список счетов пользователей с возможностью фильтрации и сортировки
    """

    permission_classes = (IsAuthenticated, IsAdminUser)
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ["created", "balance"]
    filterset_class = AccountFilter
    pagination = AccountPagination

    def get_queryset(self) -> QuerySet[Account]:
        return Account.objects.all()

    def get_serializer_class(self) -> type[AccountSerializer | UpdateBalanceSerializer]:
        if self.action == "list":
            return AccountSerializer
        elif self.action == "partial_update":
            return UpdateBalanceSerializer


@extend_schema(tags=["Admins (ЛК Администратора)"])
@extend_schema_view(
    list=extend_schema(
        summary="Список транзакций в ЛК Администратора",
    ),
)
class AdminTransactionsViewSet(GenericViewSet, ListModelMixin):
    """
    Список всех транзакций в ЛК Администатора с фильтрацией и сортировкой
    """

    permission_classes = (IsAuthenticated, IsAdminUser)
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ["created", "amount"]
    filterset_class = TranscationFilter
    pagination_class = TranscationPagination
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
