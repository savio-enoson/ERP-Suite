from django.apps import AppConfig


class PurcashingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Purchasing'

    def ready(self):
        from ERP_Harapan import signals