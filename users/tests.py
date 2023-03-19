from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from finance.models import Currency
from .models import User, UserAdditionalInfo
from .serializers import GetUserInfoSerializer


class UsersTests(APITestCase):

    def setUp(self):
        currency_data = [
            Currency(symbol='₽', code=821, short_name='RUR', full_name='Российский рубль'),
            Currency(symbol='$', code=840, short_name='USD', full_name='доллар США'),
            Currency(symbol='€', code=978, short_name='EUR', full_name='евро'),
            Currency(symbol='¥', code=156, short_name='CNY', full_name='Китайский юань'),
        ]
        Currency.objects.bulk_create(currency_data)

        self.user_1 = User.objects.create_user(
            username='user1@mail.ru',
            password='qwerty123456',
            first_name='Иван',
            middle_name='Иванович',
            last_name='Иванов',
            phone='+79999999999',
        )
        self.user_1.save()

        UserAdditionalInfo.objects.create(
            user=self.user_1,
            date_of_birth='1990-12-12',
            registered_address='Москва, Валовая 18-156',
            passport_series='5656',
            passport_number='121212',
            subdivision_code='777-777',
            date_of_issue='2004-12-12',
        )

        self.user_1_token = Token.objects.create(user=self.user_1)

    def test_user_signup(self):
        """Регистрация пользователя"""

        data = {
            "username": "user2333333@example.com",
            "password": "string777777",
            "first_name": "string",
            "last_name": "string",
            "middle_name": "string",
            "phone": "+79068187313",
            "sms_notification": True,
            "userinfo": {
                "date_of_birth": "2023-03-14",
                "sex": "Муж",
                "registered_address": "string",
                "passport_series": "2222",
                "passport_number": "232323",
                "subdivision_code": "777-777",
                "date_of_issue": "2023-03-14"
            }
        }
        response = self.client.post('/api/v1/users/signup', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        """Авторизация пользователя"""

        data = {
            "username": 'user1@mail.ru',
            "password": 'qwerty123456',
        }
        response = self.client.post('/auth/token/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('auth_token' in response.json())

    def test_user_logout(self):
        """Логаут пользователя"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        response = self.client.post('/auth/token/logout/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_user_info(self):
        """Вывод информации о пользователе"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        response = self.client.get(f'/api/v1/users/area/{self.user_1.id}/')
        serializer_data = GetUserInfoSerializer(self.user_1).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_update_user_info(self):
        """Изменение информации о пользователе"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        updated_data = {
            "first_name": "Иван1",
            "last_name": "Иванов1",
            "middle_name": "Иванович1",
            "phone": "+79999999991",
            "sms_notification": False,
            "userinfo": {
                "date_of_birth": "1990-11-12",
                "sex": "Муж",
                "registered_address": "string",
                "passport_series": "1111",
                "passport_number": "222222",
                "subdivision_code": "999-999",
                "date_of_issue": "2023-03-14"
            }
        }

        response = self.client.patch(f'/api/v1/users/area/{self.user_1.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
