from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.db.models import F, Q

from finance.models import Currency, Account, Transaction
from finance.serializers import AccountSerializer, TransactionSerializer
from users.models import User, UserAdditionalInfo


class FinanceTests(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(
            username='user1@mail.ru',
            password='qwerty123456',
            first_name='Иван',
            middle_name='Иванович',
            last_name='Иванов',
            phone='+79999999999',
        )

        self.user_2 = User.objects.create_user(
            username='user2@mail.ru',
            password='qwerty1234569',
            first_name='Петр',
            middle_name='Петрович',
            last_name='Петров',
            phone='+79999999998',
        )

        UserAdditionalInfo.objects.create(
            user=self.user_1,
            date_of_birth='1990-12-12',
            registered_address='Москва, Валовая 18-156',
            passport_series='5656',
            passport_number='121212',
            subdivision_code='777-777',
            date_of_issue='2004-12-12',
        )

        UserAdditionalInfo.objects.create(
            user=self.user_2,
            date_of_birth='1990-11-11',
            registered_address='Москва, Королева 15-112',
            passport_series='4545',
            passport_number='373737',
            subdivision_code='999-999',
            date_of_issue='2003-10-10',
        )

        account_user_1_rur = Account.objects.get(user=self.user_1, сurrency_id='1')
        account_user_2_rur = Account.objects.get(user=self.user_2, сurrency_id='1')
        account_user_1_usd = Account.objects.get(user=self.user_1, сurrency_id='2')
        account_user_2_usd = Account.objects.get(user=self.user_2, сurrency_id='2')

        transactions = [
            Transaction(
                sender_account=account_user_1_rur,
                reciever_account=account_user_2_rur,
                currency_id=1,
                description='Перевод средств',
                amount=100,
                transaction_type=Transaction.DEBIT,
            ),
            Transaction(
                sender_account=account_user_1_rur,
                reciever_account=account_user_2_rur,
                currency_id=1,
                description='Перевод средств',
                amount=10,
                transaction_type=Transaction.DEBIT,
            ),
            Transaction(
                sender_account=account_user_1_usd,
                reciever_account=account_user_2_usd,
                currency_id=2,
                description='Перевод средств',
                amount=100,
                transaction_type=Transaction.DEBIT,
            ),
            Transaction(
                sender_account=account_user_1_usd,
                reciever_account=account_user_2_usd,
                currency_id=2,
                description='Перевод средств',
                amount=10,
                transaction_type=Transaction.DEBIT,
            ),
        ]

        Transaction.objects.bulk_create(transactions)

        self.user_1_token = Token.objects.create(user=self.user_1)
        self.user_2_token = Token.objects.create(user=self.user_2)

        Account.objects.filter(user=self.user_1, сurrency_id='1').update(balance=100)

    def test_user_account_list(self):
        """Список счетов пользователя"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        response = self.client.get(f'/api/v1/finance/user_account/')
        serializer_data = AccountSerializer(Account.objects.filter(user=self.user_1), many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_transfer_funds_counterparty(self):
        """Перевед средств другому пользователю"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        senders_account = Account.objects.get(user=self.user_1, сurrency_id='1')
        receivers_account = Account.objects.get(user=self.user_2, сurrency_id='1')
        senders_old_balance = senders_account.balance
        receivers_old_balance = receivers_account.balance

        data = {
            "senders_account": senders_account.number,
            "amount_to_send": "100",
            "receivers_account": receivers_account.number,
            "amount_to_receive": "100",
            "receiver_type": "counterparty",
        }

        response = self.client.post('/api/v1/finance/user_transaction/transfer_funds/', data, format='json')
        senders_new_balance = Account.objects.get(number=senders_account.number).balance
        receivers_new_balance = Account.objects.get(number=receivers_account.number).balance
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(senders_old_balance - 100, senders_new_balance)
        self.assertEqual(receivers_old_balance + 100, receivers_new_balance)

    def test_get_rates(self):
        """Получение курсов валют"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        response = self.client.get(f'/api/v1/finance/user_transaction/get_rates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue({'USD', 'EUR', 'CNY'}.issubset(response.json()))

    def test_get_user_transactions(self):
        """Получить историю транзакций пользователя"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        response = self.client.get(f'/api/v1/finance/user_transaction/')
        serializer_data = TransactionSerializer(Transaction.objects.filter(
            Q(sender_account__user=self.user_1, transaction_type=Transaction.DEBIT) |
            Q(reciever_account__user=self.user_1, transaction_type=Transaction.CREDIT)
        ).order_by('-created')[:2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer_data)

    def test_get_user_transactions_filtred(self):
        """Получить историю транзакций пользователя отфильтрованных по типу валюты, сумме, типу транзакции"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        response = self.client.get(f'/api/v1/finance/user_transaction/?transaction_type=credit&currency=RUR&amount=100')
        serializer_data = TransactionSerializer(
            Transaction.objects.filter(
                Q(sender_account__user=self.user_1, transaction_type=Transaction.DEBIT) |
                Q(reciever_account__user=self.user_1, transaction_type=Transaction.CREDIT),
                transaction_type=Transaction.CREDIT,
                currency__short_name='RUR',
                amount=100,
            ).order_by('-created'), many=True
        ).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer_data)

    def test_create_refill_application(self):
        """Создание заявки на пополнение счета"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        data = {
            "amount": "30",
            "type": "refill"
        }
        response = self.client.post('/api/v1/finance/user_application/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('confirmation_url' in response.json())
