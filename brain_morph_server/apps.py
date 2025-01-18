from django.apps import AppConfig


class BrainMorphServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'brain_morph_server'

    def ready(self) -> None:
        from brain_morph_server.utils.PermissionUtils import generate_permissions
        try:
            generate_permissions()
        except Exception as e:
            print(e)
        return super().ready()
