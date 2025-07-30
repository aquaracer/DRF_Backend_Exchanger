from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User, UserAdditionalInfo


class UserAdditionalInfoSerializer(serializers.ModelSerializer):
    """Дополнительная информация о пользователе"""

    class Meta:
        model = UserAdditionalInfo
        exclude = ("user",)


class CreateUserSerializer(serializers.ModelSerializer):
    """Регистрация пользователя"""

    userinfo = UserAdditionalInfoSerializer()
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "sms_notification",
            "userinfo",
        )
        extra_kwargs = {
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone": {"required": True},
        }

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": _("Пароли не совпадают")}
            )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        """Создание пользователя с дополнительной информацией"""

        userinfo_data = validated_data.pop("userinfo")
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        UserAdditionalInfo.objects.create(user=user, **userinfo_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Информация о пользователе"""

    additional_user_info = serializers.SerializerMethodField("get_additional_user_info")

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "sms_notification",
            "additional_user_info",
        )

    def get_additional_user_info(self, obj: User) -> dict[str, Any] | None:
        if UserAdditionalInfo.objects.filter(user=obj).exists():
            return UserAdditionalInfoSerializer(
                UserAdditionalInfo.objects.get(user=obj)
            ).data


class UpdateUserSerializer(UserSerializer):
    """Изменение информации о пользователе"""

    def update(self, instance, validated_data):
        if "userinfo" in validated_data:
            nested_serializer = self.fields["userinfo"]
            nested_instance = instance.useradditionalinfo
            nested_data = validated_data.pop("userinfo")
            nested_serializer.update(nested_instance, nested_data)

        return super().update(instance, validated_data)
