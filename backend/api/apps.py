from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' #Done
    name = 'api' # This should be the simple app name
    verbose_name = "RAG API"