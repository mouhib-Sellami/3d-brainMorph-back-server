import logging
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from . import serializers
from rest_framework.permissions import IsAuthenticated
from brain_morph_server import models
from brain_morph_server.utils.decorators import has_permission
from django.http import HttpResponse
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
import json
from brain_morph_server.utils.brainMorph_bucket import upload_single, create_folder
from brain_morph_server import views
CONTENT_TYPE = 'application/json'

logger = logging.getLogger('brain_morph')


class PatientViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PatientSerializer
    queryset = models.Patient.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.PatientSerializer
        return serializers.PatientCreateSerializer

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

    @has_permission("can_change_patient")
    @action(methods=['POST'], url_path="upload", url_name="upload", detail=True)
    def upload(self, request, pk=None):
        try:
            patient = models.Patient.objects.get(pk=pk)
            create_folder(patient.folder_name)
            for count, x in enumerate(request.FILES.getlist("files")):
                upload_single(x, patient.folder_name)
            patient.has_files = True
            patient.save(update_fields=['has_files'])

            return HttpResponse(json.dumps(serializers.PatientSerializer(patient).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @has_permission("can_change_patient")
    @action(methods=['POST'], url_path="start-patient", url_name="start-patient", detail=True)
    def start_patient(self, request, pk=None):
        try:
            patient = models.Patient.objects.get(pk=pk)
            job = models.JobClientArtifact()
            job.patient = patient
            job.save()
            views.engine_download_artifact.add_task(job=job, new=True,delete_when_finish=False)
            return HttpResponse(json.dumps(serializers.PatientSerializer(patient).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)
