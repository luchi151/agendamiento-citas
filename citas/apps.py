from django.apps import AppConfig


class CitasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'citas'
    verbose_name = 'Sistema de Citas'
    
    def ready(self):
        """Se ejecuta cuando Django inicializa la app"""
        # Importar signals para registrarlos
        import citas.signals  # noqa
