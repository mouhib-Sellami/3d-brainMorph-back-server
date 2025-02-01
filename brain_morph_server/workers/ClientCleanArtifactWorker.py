import os
import shutil
import json
from engine.conf.Worker import Worker
from engine.models import FailedTask, Task
from brain_morph_server import models
from brain_morph_server.utils import brainMorph_bucket
from brainMorph_back_server.socket_handler import sio
from brain_morph_server.viewsets.serializers import PatientSerializer
import time
import psutil


class ClientCleanArtifactWorker(Worker):
    def on_exception_callback(self, task: Task, exception: Exception):
        super().on_exception_callback(task, exception)

    def on_failed_callback(self, failed_task: FailedTask, exception: Exception):
        job: models.JobClientArtifact = failed_task.task.job_payload
        patient: models.Patient = job.patient
        patient.is_processing = False
        patient.save(update_fields=['is_processing'])
        super().on_failed_callback(failed_task, exception)

    def on_finish_callback(self, task: Task):
        super().on_finish_callback(task)

    def worker_runner(self, task: Task):
        super().worker_runner(task)

        job: models.JobClientArtifact = task.job_payload
        patient: models.Patient = job.patient

        tumor_file_name = patient.tumor_file_path.split(os.sep)[-1]

        brainMorph_bucket.upload_single_with_file_path(
            patient.tumor_file_path, tumor_file_name, patient.folder_name)

        nii_file_name = patient.nii_file_path.split(os.sep)[-1]

        brainMorph_bucket.upload_single_with_file_path(
            patient.nii_file_path, nii_file_name, patient.folder_name)

        brain_combine_file_name = patient.brain_combine_file_path.split(
            os.sep)[-1]

        brainMorph_bucket.upload_single_with_file_path(
            patient.brain_combine_file_path, brain_combine_file_name, patient.folder_name)

        brain_file_name = patient.brain_file_path.split(os.sep)[-1]
        brainMorph_bucket.upload_single_with_file_path(
            patient.brain_file_path, brain_file_name, patient.folder_name)

        patient.nii_file_path = brainMorph_bucket.BUCKET + \
            "/"+str(patient.folder_name) + "/" + nii_file_name

        patient.tumor_file_path = brainMorph_bucket.BUCKET + "/"+str(
            patient.folder_name) + "/" + tumor_file_name

        patient.brain_file_path = brainMorph_bucket.BUCKET + "/"+str(
            patient.folder_name) + "/" + brain_file_name

        patient.brain_combine_file_path = brainMorph_bucket.BUCKET + "/"+str(
            patient.folder_name) + "/" + brain_combine_file_name

        patient.is_processing = False
        patient.is_generated = True

        patient.save(update_fields=['nii_file_path', 'tumor_file_path',
                     'brain_combine_file_path', 'brain_file_path', 'is_generated', 'is_processing'])
        sio.emit("patient_complete", json.dumps(
            PatientSerializer(patient).data))
        if os.path.exists(job.download_folder_path):
            shutil.rmtree(job.download_folder_path)
