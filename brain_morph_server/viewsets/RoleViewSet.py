import logging
from rest_framework.viewsets import ModelViewSet
from . import serializers
from rest_framework.permissions import IsAuthenticated
from brain_morph_server import models
from brain_morph_server.utils.decorators import has_permission
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import status

logger = logging.getLogger('brain_morph')
CONTENT_TYPE = 'application/json'


class RoleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.RoleReadSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.RoleReadSerializer
        return serializers.RoleCreateSerializer

    def get_queryset(self):
        return models.Role.objects.all()

    @has_permission("can_view_role")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("can_create_role")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("can_change_role")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("can_delete_role")
    def destroy(self, request, *args, **kwargs):
        try:
            role = models.Role.objects.get(pk=kwargs["pk"])
            if role.can_delete:
                return super().destroy(request, *args, **kwargs)
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist:
            return super().destroy(request, *args, **kwargs)

    @has_permission("can_view_role")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("can_change_role")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
