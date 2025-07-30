import uuid

from rest_framework import status

from common.exceptions import HTTPException


class YookassaPaymentCreateError(HTTPException):
    def __init__(self, error: str) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = f"Yookassa API error: Payment creation failed {error}"


class YookassaWebhookJsonDecodeError(HTTPException):
    def __init__(self, error: str) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"JSONDecodeError: Failed to parse Yookassa webhook JSON:{error}"


class YookassaWebhookDataStructureError(HTTPException):
    def __init__(self, error: str) -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"Invalid Yookassa webhook data structure:{error}"


class YookassaWebhookUnexpectedError(HTTPException):
    def __init__(self, error: str) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = f"Unexpected error during Yookassa webhook processing:{error}"


class PaymentIdExtractionError(HTTPException):
    def __init__(self, error: str) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = (f"Invalid notification object structure for payment ID "
                       f"extraction:{error}")


class ApplicationRefillNotFoundError(HTTPException):
    def __init__(self, error: str) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = (f"Invalid notification object structure for payment ID "
                       f"extraction:{error}")


class YookassaPyamentConfirmationError(HTTPException):
    def __init__(self, payment_id: uuid, error: str) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = f"Failed to confirm payment {payment_id} with Yookassa: {error}"


class YookassaPaymentStatusCheckError(HTTPException):
    def __init__(self, payment_id: uuid, error: str) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = f"Yookassa payment status check failed for {payment_id}: {error}"


class YookassaPaymentFinalizeError(HTTPException):
    def __init__(self, payment_id: uuid) -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = (f"Yookassa error: Payment {payment_id} failed to finalize as "
                       f"'succeeded'.")
