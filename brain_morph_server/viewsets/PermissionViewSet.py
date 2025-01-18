import logging
from rest_framework.viewsets import ReadOnlyModelViewSet
from . import serializers
from rest_framework.permissions import IsAuthenticated
from brain_morph_server import models

logger = logging.getLogger('sky_forge')


class PermissionViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AppPermissionSerializer
    queryset = models.AppPermission.objects.all()
