from rest_framework.pagination import PageNumberPagination

class TranscationPagination(PageNumberPagination):
    """Пагинация списка транзакций"""

    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 50


class AccountPagination(PageNumberPagination):
    """Пагинация списка счетов"""

    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 50