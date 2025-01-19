import logging
from rest_framework.viewsets import ModelViewSet
from . import serializers
from rest_framework.permissions import IsAuthenticated
from brain_morph_server import models
from brain_morph_server.utils.decorators import has_permission

logger = logging.getLogger('brain_morph')

class PatientViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PatientSerializer
    queryset = models.Patient.objects.all()

    @has_permission("can_view_patient")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("can_create_patient")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("can_change_patient")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("can_delete_patient")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @has_permission("can_view_patient")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("can_change_patient")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
