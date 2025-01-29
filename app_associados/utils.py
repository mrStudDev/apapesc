from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configurações de autenticação
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'app_associados/credentials/service_account.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)

def create_associado_folder(folder_name, parent_folder_id):
    """
    Cria uma pasta no Google Drive dentro de uma pasta pai específica.
    
    :param folder_name: Nome da pasta a ser criada.
    :param parent_folder_id: ID da pasta pai no Google Drive.
    :return: ID da pasta criada ou None em caso de erro.
    """
    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]  # ID da pasta "Associados"
        }
        file = service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')
    except HttpError as error:
        print(f"Erro ao criar pasta no Google Drive: {error}")
        return None