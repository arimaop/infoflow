"""
ASGI config for info_flow project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "info_flow.settings")

application = get_asgi_application()

