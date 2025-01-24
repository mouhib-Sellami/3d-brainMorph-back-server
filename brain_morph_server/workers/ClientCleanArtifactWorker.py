from engine.conf.Worker import Worker
from engine.models import FailedTask, Task
from brain_morph_server import models
from django.conf import settings
import time
from brain_morph_server import views
from brain_morph_server.utils import brainMorph_bucket
import os
import shutil
import time


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
        if os.path.exists(job.download_folder_path):
            shutil.rmtree(job.download_folder_path)
