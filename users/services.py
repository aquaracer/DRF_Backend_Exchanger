from .models import  User, UserAdditionalInfo

def signup_user(self, request):
    """Регистрация пользователя"""

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    userinfo = serializer.validated_data.pop('userinfo')
    user = User.objects.create_user(**serializer.validated_data)
    userinfo['user'] = user
    UserAdditionalInfo.objects.create(**userinfo)