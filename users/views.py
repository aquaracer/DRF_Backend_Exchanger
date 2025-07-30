from typing import Any
from urllib.request import Request

from django.db import transaction
from django.db.models import Q, QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from admins.views import AdminTransactionsViewSet
from finance.models import Account, Application, Transaction
from finance.pagination import AccountPagination
from finance.serializers import (
    AccountSerializer,
    ApplicationSerializer,
    CreateApplicationSerializer,
    CreateTransactionSerializer,
    TransactionSerializer,
)
from finance.services.finance_services import send_funds
from finance.services.yookassa import create_application, handle_yookassa_webhook

from .models import User
from .serializers import CreateUserSerializer, UpdateUserSerializer, UserSerializer


@extend_schema(tags=["Регистрация пользователя"])
@extend_schema_view(post=extend_schema(summary="Регистрация пользователя", ), )
class UserSignupView(CreateAPIView):
    """Регистрация пользователя"""

    permission_classes = [AllowAny, ]
    serializer_class = CreateUserSerializer


@extend_schema(tags=["Users (ЛК Пользователя)"])
@extend_schema_view(
    retrieve=extend_schema(
        summary="Информация о пользователе",
    ),
    partial_update=extend_schema(
        summary="Частичное изменение информации о пользователе",
        request=UpdateUserSerializer,
    ),
    update=extend_schema(
        summary="Изменение информации о пользователе", request=UpdateUserSerializer
    ),
)
class UserAreaViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """Вывод и редактирование информации о пользователе в ЛК Пользователя"""

    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self) -> UserSerializer | UpdateUserSerializer:
        if self.action == "retrieve":
            return UserSerializer
        elif self.action == "partial_update":
            return UpdateUserSerializer

    def get_queryset(self) -> list[User]:
        return User.objects.filter(id=self.request.user.id)


@extend_schema(tags=["Users (ЛК Пользователя)"])
@extend_schema_view(list=extend_schema(summary="Список счетов в ЛК Пользователя", ), )
class UserAccountListViewSet(GenericViewSet, ListModelMixin):
    """Список счетов в ЛК пользователя"""

    permission_classes = (IsAuthenticated,)
    serializer_class = AccountSerializer
    pagination = AccountPagination

    def get_queryset(self) -> QuerySet[Account]:
        return Account.objects.filter(user=self.request.user)


@extend_schema(tags=["Users (ЛК Пользователя)"])
@extend_schema_view(
    list=extend_schema(
        summary="Список транзакций в ЛК Пользователя",
    ),
)
class UserTransactionsViewSet(AdminTransactionsViewSet):
    """
    API для управления транзакциями пользователя в ЛК Пользователя.

    Предоставляет следующие возможности:
    * Список транзакций: Получение списка транзакций с возможностью фильтрации и
    сортировки.
    * Перевод средств: Перевод средств на свой собственный счет или счет контрагента.
    """

    permission_classes = (IsAuthenticated,)

    def get_serializer_class(
            self,
    ) -> type[TransactionSerializer | CreateTransactionSerializer]:
        if self.action == "transfer_funds":
            return CreateTransactionSerializer
        else:
            return TransactionSerializer

    def get_queryset(self) -> QuerySet[Transaction]:
        return (
            Transaction.objects.filter(
                Q(
                    sender_account__user=self.request.user,
                    transaction_type=Transaction.DEBIT,
                )
                | Q(
                    reciever_account__user=self.request.user,
                    transaction_type=Transaction.CREDIT,
                )
            )
            .prefetch_related("sender_account", "reciever_account")
            .order_by("-created")
        )

    @extend_schema(summary="Перевод средств")
    @action(
        detail=False,
        methods=["POST"],
        description="Перевод средств",
        url_path="transfer_funds",
        url_name="transfer_funds",
        serializer_class=CreateTransactionSerializer,
    )
    @transaction.atomic
    def transfer_funds(self, request: Request) -> Response:
        """
        Перевод средств на свой собственный счет или счет контрагента
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_funds(transfer_data=serializer.validated_data, request=request)
        return Response()


@extend_schema(tags=["Users (ЛК Пользователя)"])
@extend_schema_view(
    list=extend_schema(
        summary="Список заявок на вывод средств в ЛК пользователя",
    ),
    create=extend_schema(
        summary="Cоздание заявки на вывод средств в ЛК пользователя",
    ),
)
class UserApplicationViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
    Ввод средств в ЛК пользователя:
    - создание заявки на ввод средств
    - список завявок на ввод средств
    - обработка вебкхука
    """

    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet[Application]:
        return Application.objects.filter(account__user=self.request.user)

    def get_serializer_class(
            self,
    ) -> type[ApplicationSerializer | CreateApplicationSerializer]:
        if self.action == "create":
            return CreateApplicationSerializer
        else:
            return ApplicationSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Создание заявки на ввод средств"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = create_application(serializer=serializer, request=request)
        return Response(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Обработка вебхука")
    @action(
        detail=False,
        methods=["POST"],
        description="Обработка вебхука",
        url_path="webhook_handler",
        url_name="webhook_handler",
        serializer_class=CreateTransactionSerializer,
    )
    def webhook_handler(self, request: Request) -> Response:
        """Обработка вебхука"""

        handle_yookassa_webhook(request)
        return Response()
