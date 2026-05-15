from django.apps import AppConfig


class EnviosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'envios'
    verbose_name = 'Gestión de Envíos'

    def ready(self):
        """Conectar señales al iniciar la aplicación."""
        import envios.signals  # noqa: F401

