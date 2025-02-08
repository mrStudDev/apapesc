
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configurações de autenticação
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'app_associados/credentials/service_account.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)

import re

def format_celular_for_whatsapp(celular):
    """
    Remove caracteres especiais e retorna o número no formato correto para o WhatsApp.
    Exemplo: (48) 99999-9999 -> 5548999999999
    """
    # Remove tudo que não for número
    celular = re.sub(r'\D', '', celular)

    # Adiciona o código do país, se não estiver presente
    if not celular.startswith('55'):
        celular = f'55{celular}'

    return celular
