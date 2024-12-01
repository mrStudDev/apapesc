"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

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


application = get_wsgi_application()
