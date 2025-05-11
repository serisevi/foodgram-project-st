"""Настройки пагинации для API."""
from rest_framework.pagination import PageNumberPagination

from foodgram.constants import DEFAULT_PAGES_LIMIT


class Pagination(PageNumberPagination):
    """Кастомный класс пагинации для API проекта."""
    
    page_size_query_param = 'limit'
    page_size = DEFAULT_PAGES_LIMIT
