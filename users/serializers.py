from rest_framework import serializers
from .models import User, UserAdditionalInfo


class UserInfoSerializer(serializers.ModelSerializer):
    """Дополнительная информация о пользователе"""

    class Meta:
        model = UserAdditionalInfo
        exclude = ('user',)


class UserSerializer(serializers.ModelSerializer):
    """Cериализатор для регистрации пользователя"""

    userinfo = UserInfoSerializer()

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'middle_name',
            'phone',
            'sms_notification',
            'userinfo'
        )


class GetUserInfoSerializer(serializers.ModelSerializer):
    """Информация о пользователе"""

    userinfo = serializers.SerializerMethodField('get_userinfo')

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'middle_name',
            'phone',
            'sms_notification',
            'userinfo'
        )

    def get_userinfo(self, obj: User):
        return UserInfoSerializer(UserAdditionalInfo.objects.get(user=obj)).data


class UpdateUserInfoSerializer(UserSerializer):
    """Изменение информации о пользователе"""

    password = serializers.CharField(read_only=True)

    def update(self, instance, validated_data):
        if 'userinfo' in validated_data:
            nested_serializer = self.fields['userinfo']
            nested_instance = instance.useradditionalinfo
            nested_data = validated_data.pop('userinfo')
            nested_serializer.update(nested_instance, nested_data)

        return super(UpdateUserInfoSerializer, self).update(instance, validated_data)


