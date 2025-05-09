from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Dict, Any, Optional

User = get_user_model()


class BaseTestCase(TestCase):
    """
    Base test case that provides common functionality for all tests.
    """
    def setUp(self) -> None:
        """
        Set up test data.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )


class BaseAPITestCase(APITestCase):
    """
    Base API test case that provides common functionality for all API tests.
    """
    def setUp(self) -> None:
        """
        Set up test data and authentication.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.user)

    def get_tokens_for_user(self, user: User) -> Dict[str, str]:
        """
        Generate JWT tokens for a user.
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def authenticate_user(self, user: User) -> None:
        """
        Authenticate a user with JWT tokens.
        """
        tokens = self.get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')

    def authenticate_admin(self) -> None:
        """
        Authenticate the admin user.
        """
        self.authenticate_user(self.admin_user)

    def assert_response_ok(self, response: Any) -> None:
        """
        Assert that the response is successful.
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def assert_response_created(self, response: Any) -> None:
        """
        Assert that the response indicates successful creation.
        """
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def assert_response_bad_request(self, response: Any) -> None:
        """
        Assert that the response indicates a bad request.
        """
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def assert_response_unauthorized(self, response: Any) -> None:
        """
        Assert that the response indicates unauthorized access.
        """
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assert_response_forbidden(self, response: Any) -> None:
        """
        Assert that the response indicates forbidden access.
        """
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def assert_response_not_found(self, response: Any) -> None:
        """
        Assert that the response indicates resource not found.
        """
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 