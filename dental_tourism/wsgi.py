"""
WSGI config for dental_tourism project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_tourism.settings')

application = get_wsgi_application()

# Dosya seed'leri (blog, çeviriler) deploy'a bağımlı olmadan, süreç açılınca arka planda (apps/core/boot.py)
from apps.core.boot import start_boot_seeds  # noqa: E402

start_boot_seeds()
