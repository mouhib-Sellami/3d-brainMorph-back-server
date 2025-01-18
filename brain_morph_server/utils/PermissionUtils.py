from brain_morph_server import models

MODEL_ACTIONS = ["create", "view", "change", "delete"]


def generate_permissions():
    models_list = ["user", "patient","role"]
    for model in models_list:
        for action in MODEL_ACTIONS:
            permission = "can_" + action + "_" + model
            permission = permission.upper()
            permission_dict = {"label": permission}
            models.AppPermission.objects.update_or_create(
                defaults=permission_dict, **permission_dict)
