from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from finance.services import finance_services


@extend_schema(
    tags=["Rates"],
    operation_id="get_rates",
    summary="Получить курсы валют",
    description="Возвращает актуальные курсы валют.",
)
@api_view(["GET"], )
@permission_classes([IsAuthenticated])
def get_rates(request: Request) -> Response:
    """Получить курсы валют"""

    rates = finance_services.get_exchange_rates()
    return Response(data=rates)
