import logging
import secrets
import json
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from . import serializers
from rest_framework.permissions import IsAuthenticated
from brain_morph_server import models
from brain_morph_server.utils.decorators import has_permission
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger('brain_morph')
CONTENT_TYPE = 'application/json'


class UserViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.UserSerializer
        elif 'update' in self.action:
            return serializers.UserCreateSerializer
        else:
            return serializers.UserCreateSerializer

    def get_queryset(self):
        return models.User.objects.all()

    @has_permission("can_view_user")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("can_create_user")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("can_change_user")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("can_delete_user")
    def destroy(self, request, *args, **kwargs):
        try:
            user = models.User.objects.get(
                pk=kwargs['pk'])
            user.is_active = False
            user.save(update_fields=['is_active'])
            return HttpResponse(status=status.HTTP_204_NO_CONTENT, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)

        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @has_permission("can_view_user")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("can_change_user")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @has_permission("can_change_user")
    @action(detail=True, url_path="activate", url_name="activate", methods=['PATCH'])
    def activate(self, request, pk=None):
        try:
            user = models.User.objects.get(pk=pk)
            user.is_active = True
            user.save(update_fields=['is_active'])
            return HttpResponse(json.dumps(serializers.UserSerializer(user).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)
