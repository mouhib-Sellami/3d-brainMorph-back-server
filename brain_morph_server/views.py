from engine.core.Engine import Engine
from engine.conf import TASK_TYPE
from brain_morph_server import models
from brainMorph_back_server.model import brain_morph_model

model = brain_morph_model.init_model()

engine_download_artifact = Engine(task_type=TASK_TYPE.download)
engine_process_mask = Engine(task_type=TASK_TYPE.process_mask)
engine_process_brain = Engine(task_type=TASK_TYPE.process_brain)
# engine_generate_rapport = Engine(task_type=TASK_TYPE.generate_rapport)
engine_clear_artifact = Engine(task_type=TASK_TYPE.clean)

# download_folder("13280c41-bfa8-4f22-b447-1dd4c48924a6")
