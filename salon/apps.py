from django.apps import AppConfig


class SalonConfig(AppConfig):
    name = "salon"
    verbose_name = "Салон связи"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from .admin_auth import register_admin_auth_urls

        register_admin_auth_urls()
