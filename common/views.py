from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from typing import Any, List, Type, Optional


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base viewset that provides common functionality for all model viewsets.
    """
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = []
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self) -> Any:
        """
        Return only active objects by default.
        """
        return self.queryset.filter(is_active=True)

    def perform_create(self, serializer: Any) -> None:
        """
        Create a new instance with the current user as creator.
        """
        serializer.save()

    def perform_update(self, serializer: Any) -> None:
        """
        Update an existing instance.
        """
        serializer.save()

    def perform_destroy(self, instance: Any) -> None:
        """
        Soft delete the instance instead of hard delete.
        """
        instance.soft_delete()

    @action(detail=True, methods=['post'])
    def restore(self, request: Any, pk: Optional[str] = None) -> Response:
        """
        Restore a soft-deleted instance.
        """
        instance = self.get_object()
        instance.restore()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def deleted(self, request: Any) -> Response:
        """
        List all soft-deleted instances.
        """
        queryset = self.queryset.filter(is_active=False)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self) -> List[Any]:
        """
        Return the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes] 