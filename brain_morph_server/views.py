from engine.core.Engine import Engine
from engine.conf import TASK_TYPE
from brain_morph_server import models

engine_download_artifact = Engine(task_type=TASK_TYPE.download)
engine_clear_artifact = Engine(task_type=TASK_TYPE.clean)

# patient = models.Patient.objects.get(pk=2)
# job = models.JobClientArtifact()
# job.patient = patient
# job.save()
# engine_download_artifact.add_task(
#     job=job,
#     delete_when_finish=False
# )
# download_folder("13280c41-bfa8-4f22-b447-1dd4c48924a6")
