import json
from engine.conf.Worker import Worker
from engine.models import FailedTask, Task
from brain_morph_server import models
from brain_morph_server import views
from brain_morph_server.utils import brainMorph_bucket
from brainMorph_back_server.socket_handler import sio
from brain_morph_server.viewsets.serializers import PatientSerializer


class ClientArtifactWorker(Worker):
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
        patient.is_processing = True
        patient.save(update_fields=['is_processing'])
        sio.emit('patient_start', json.dumps(PatientSerializer(patient).data))
        folder_name = patient.folder_name
        folder_path = brainMorph_bucket.download_folder(str(folder_name))
        if folder_path:
            job.download_folder_path = folder_path
            job.save(update_fields=['download_folder_path'])
            views.engine_process_mask.add_task(
                task=task, new=True, delete_when_finish=False)
        else:
            raise Exception("cannot download artifacts")
