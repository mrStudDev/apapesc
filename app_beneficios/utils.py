# app_beneficios/utils.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from django.conf import settings

def upload_to_drive(caminho_local, nome_arquivo, folder_id):
    """Envia arquivo para o Google Drive na pasta do associado."""
    credentials = service_account.Credentials.from_service_account_file(
        str(settings.GOOGLE_DRIVE_CREDENTIALS_PATH),  # 💡 Corrigido!
        scopes=['https://www.googleapis.com/auth/drive.file']
    )

    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': nome_arquivo,
        'parents': [folder_id]
    }

    media = MediaFileUpload(caminho_local, resumable=True)

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return uploaded_file.get('id')
