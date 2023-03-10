from rest_framework import serializers, status

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

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class APIExceptionBase(Exception):

    status_code: int

    def __init__(self, message: str, code: str):
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