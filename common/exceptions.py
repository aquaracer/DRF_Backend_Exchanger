from rest_framework import serializers, status
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ErrorSerializer(serializers.Serializer):
    """Бизнес-ошибка"""

    error_code = serializers.CharField(
        help_text='Код ошибки',
        required=True,
        max_length=40,
    )
    error_message = serializers.CharField(
        help_text='Краткое описание ошибки',
        required=True,
        max_length=255,
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ErrorResponseSerializer(serializers.Serializer):
    """Стандартная ошибка"""

    error = ErrorSerializer()

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        pass

    def create(self, validated_data: Dict[str, Any]) -> Any:
        pass


class APIExceptionBase(Exception):
    status_code: int

    def __init__(self, message: str, code: str) -> None:
        if not self.status_code:
            raise NotImplementedError('status_code is not set')

        self.serializer = ErrorResponseSerializer(
            {
                'error': {
                    'error_code': code,
                    'error_message': message,
                },
            }
        )


class BadRequest(APIExceptionBase):
    status_code = status.HTTP_400_BAD_REQUEST


class BaseAPIException(Exception):
    """
    Base exception class for API exceptions.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('A server error occurred.')
    default_code = 'error'

    def __init__(self, detail: Optional[str] = None, code: Optional[str] = None) -> None:
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        self.detail = {
            'error': detail,
            'code': code
        }


class ValidationAPIException(BaseAPIException):
    """
    Exception for validation errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid input.')
    default_code = 'invalid'


class AuthenticationAPIException(BaseAPIException):
    """
    Exception for authentication errors.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Authentication credentials were not provided.')
    default_code = 'not_authenticated'


class PermissionAPIException(BaseAPIException):
    """
    Exception for permission errors.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('You do not have permission to perform this action.')
    default_code = 'permission_denied'


class NotFoundAPIException(BaseAPIException):
    """
    Exception for not found errors.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Not found.')
    default_code = 'not_found'


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Add additional information to the response
        if isinstance(response.data, dict):
            response.data = {
                'error': response.data.get('detail', str(response.data)),
                'code': response.data.get('code', 'error')
            }
        else:
            response.data = {
                'error': str(response.data),
                'code': 'error'
            }

    # Handle Django's ValidationError
    if isinstance(exc, ValidationError):
        response = {
            'error': str(exc),
            'code': 'validation_error'
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # Handle Django's IntegrityError
    if isinstance(exc, IntegrityError):
        response = {
            'error': 'Database integrity error occurred.',
            'code': 'integrity_error'
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # Log unhandled exceptions
    if response is None:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        response = {
            'error': 'An unexpected error occurred.',
            'code': 'unexpected_error'
        }
        return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response