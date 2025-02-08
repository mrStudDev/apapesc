import os
from googleapiclient.discovery import build
from google.oauth2 import service_account


SCOPES = ['https://www.googleapis.com/auth/drive']
# Caminho do arquivo JSON da conta de serviço
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'credentials/service_account.json')

# ID da pasta raiz onde serão criadas as pastas dos associados
PARENT_FOLDER_ID = "15Nby8u0aLy1hcjvfV8Ja6w_nSG0yFQ2w?lfhs=2"  # Removido o sufixo ?lfhs=2

# Autenticação com o Google Drive API
def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

# Criar uma pasta no Google Drive para um novo associado
def create_associado_folder(nome_associado, parent_folder_id):
    try:
        drive_service = get_drive_service()
        folder_metadata = {
            "name": nome_associado,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id]
        }
        folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
        folder_id = folder.get("id")
        if not folder_id:
            raise ValueError("Nenhum ID de pasta retornado.")
        
        print(f"Pasta criada com sucesso: {folder_id}")
        return folder_id
    except Exception as e:
        print(f"Erro ao criar pasta no Drive: {e}")
        return None