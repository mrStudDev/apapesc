import os
from googleapiclient.discovery import build
from google.oauth2 import service_account


# jhkjdhksf
# Caminho do arquivo JSON da conta de serviço
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'config/drive_credentials.json')

# ID da pasta raiz onde serão criadas as pastas dos associados
PARENT_FOLDER_ID = "1AbCDEFGHIJK"  # Altere para o ID da sua pasta no Drive

# Autenticação com o Google Drive API
def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

# Criar uma pasta no Google Drive para um novo associado
def create_associado_folder(nome_associado):
    drive_service = get_drive_service()
    folder_metadata = {
        "name": nome_associado,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [PARENT_FOLDER_ID]  # Define a pasta raiz onde será criada
    }
    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    return folder.get("id")  # Retorna o ID da nova pasta criada
