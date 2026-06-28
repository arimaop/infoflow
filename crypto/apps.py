from django.apps import AppConfig


class CryptoConfig(AppConfig):
    name = 'crypto'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from .admin_auth import register_admin_auth_urls

        register_admin_auth_urls()
