#app_documentos/
# # google_drive_integration.py

# google_drive_integration.py

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Caminho até o JSON localizado em app_associados/credentials/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'app_associados', 'credentials', 'service_account.json')

SCOPES = ['https://www.googleapis.com/auth/drive.file']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

drive_service = build('drive', 'v3', credentials=credentials)

def upload_to_drive(local_path, nome_arquivo, folder_id):
    file_metadata = {
        'name': nome_arquivo,
        'parents': [folder_id]
    }
    media = MediaFileUpload(local_path, resumable=True)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return uploaded_file.get('id')

