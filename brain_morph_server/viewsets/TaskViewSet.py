import logging
from rest_framework.viewsets import ReadOnlyModelViewSet
from . import serializers
from rest_framework.permissions import IsAuthenticated
from engine import models as engineModels

logger = logging.getLogger('brain_morph')


class TaskViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TaskSerializer
    queryset = engineModels.Task.objects.all().order_by("-created_at")
