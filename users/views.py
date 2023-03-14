from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import User
from .serializers import UserSerializer, GetUserInfoSerializer, UpdateUserInfoSerializer
from backend_exchanger.swagger_schema import TOKENS_PARAMETER
from .services import signup_user


@method_decorator(name='create', decorator=swagger_auto_schema(tags=['signup']))
class UserSignupView(CreateAPIView):
    """Регистрация пользователя"""

    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        signup_user(self, request)
        return Response(status=status.HTTP_201_CREATED)


@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    tags=['users'], **TOKENS_PARAMETER, operation_description='Изменение информации о пользователе'))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    tags=['users'], **TOKENS_PARAMETER, operation_description='Вывод информации о пользователе'))
class UserAreaViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """
    Вывод и редактирование информации о пользователе в личном кабинете пользователя
    """
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GetUserInfoSerializer
        elif self.action == 'partial_update':
            return UpdateUserInfoSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response()

