from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configurações de autenticação
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'app_associados/credentials/service_account.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)

def list_drive_folders():
    try:
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields="nextPageToken, files(id, name)").execute()
        
        items = results.get('files', [])
        if not items:
            print('Nenhuma pasta encontrada.')
        else:
            print('Pastas disponíveis:')
            for item in items:
                print(f"{item['name']} ({item['id']})")
    except HttpError as error:
        print(f"Erro ao listar pastas: {error}")
        
results = service.files().list(
    q="",
    spaces='drive',
    fields="nextPageToken, files(id, name, mimeType)").execute()

# Teste: listar pastas
list_drive_folders()
