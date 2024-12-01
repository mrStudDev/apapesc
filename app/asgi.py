"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

import os

"""
    RODAR COMANDOS NO TERMINAL PARA CONFIGURAR O MANAGE.PY
    export ENV_TYPE=local
    export ENV_TYPE=production
"""


env_type = os.getenv('ENV_TYPE', 'local')  # Padrão é 'local'

if env_type == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings_production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings_local')


application = get_asgi_application()
