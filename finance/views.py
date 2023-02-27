from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from django.db.models import Q
from django.db import transaction
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from backend_exchanger.swagger_schema import TOKENS_PARAMETER
from .serializers import AccountSerializer, TransactionSerializer, YourselfTransactionSerializer, \
    UpdateBalanceSerializer
from .models import Account, Transaction
from .filters import TranscationFilter, AccountFilter
from .services import send_funds, TranscationPagination


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['worker'], operation_description='Получение списка счетов пользователя', ** TOKENS_PARAMETER))
class UserAccountListViewSet(GenericViewSet, ListModelMixin):
    """Получения списка счетов пользователя"""

    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['Transaction'], operation_description='Получение списка всех транзакций в личном кабинете Администратора',
    **TOKENS_PARAMETER))
class AdminTransactionsViewSet(GenericViewSet, ListModelMixin):
    """
    Список всех транзакций в личном кабинете Администатора.
    Фильтрации по следующим параметрам:
    - Валюты
    - Тип транзакции
    - Сумма транзакции
    - Диапазон сумм для транзакции
    - Дата создания транзакции
    - Диапазон дат транзакций
    - Счет отправителя
    - Счет получателя

    Сортировка по следующим параметрам:
    - Дата создания
    - Сумма транзакции
    """

    permission_classes = (IsAuthenticated,)
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['created', 'amount']
    filterset_class = TranscationFilter
    pagination_class = TranscationPagination

    def get_queryset(self):
        return Transaction.objects.all()

    def get_serializer_class(self):
        return TransactionSerializer


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['Transaction'], operation_description='Получение списка счетов пользователя', **TOKENS_PARAMETER))
class UserTransactionsViewSet(AdminTransactionsViewSet):
    """
    Транзакции в личном кабинете Юзера.
    Фильтрация, сортировка и пагинация наследуется от родительского класса.
    Метод list отображает список всех транзакций текущего пользователя.
    Метод transfer_funds осуществяет перевод средств (на свой счет или счет контрагента)
    """

    def get_serializer_class(self):
        if self.action == 'transfer_funds_yourself':
            return YourselfTransactionSerializer
        else:
            return TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(sender_account__user=self.request.user, transaction_type=Transaction.DEBIT) |
            Q(reciever_account__user=self.request.user, transaction_type=Transaction.CREDIT)
        ).order_by('-created')

    @swagger_auto_schema(method='POST', tags=['Transaction'],
                         serializer_class=YourselfTransactionSerializer, **TOKENS_PARAMETER)
    @action(detail=False, methods=['POST'])
    @transaction.atomic
    def transfer_funds(self, request):
        """
        Перевод средств. В зависимости от параметра receiver_type средства переводятся себе или другому пользователю
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_funds(serializer)
        return Response()


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['Administrator'], operation_description='Получение списка счетов пользователя', **TOKENS_PARAMETER))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    tags=['Administrator'], operation_description='Пополнение баланса пользователя', **TOKENS_PARAMETER))
class AdminAccountsViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin):
    """
    Счета пользователей в личном кабинете Администратора
    методы:
    partial_update - изменение баланса счета
    list - список счетов пользователей с возможностью фильтрации и сортировки
    Фильтрация по следующим параметрам:
    - Валюты
    - Баланс
    - Диапазон сумм на балансе
    - Номер счета
    - Логин пользователя

    Сортировка по следующим параметрам:
    - Дата создания
    - Баланс
    """

    permission_classes = (IsAuthenticated,)
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ['created', 'balance']
    filterset_class = AccountFilter
    pagination = TranscationPagination

    def get_queryset(self):
        return Account.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountSerializer
        elif self.action == 'partial_update':
            return UpdateBalanceSerializer
