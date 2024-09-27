# ventas/apps.py

from django.apps import AppConfig

class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas'

    def ready(self):
        import ventas.signals  # Importa las señales para que se conecten
