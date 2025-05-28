 #app_beneficios/utils.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from django.conf import settings
from app_beneficios.models import LevaProcessamentoBeneficio, ControleBeneficioModel, ControleLevaItem

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

def criar_leva(beneficio, user):
    leva = LevaProcessamentoBeneficio.objects.create(
        beneficio=beneficio,
        criado_por=user
    )

    controles = ControleBeneficioModel.objects.filter(
        beneficio=beneficio
    ).order_by(
        'associado__user__first_name',
        'associado__user__last_name'
    )

    for controle in controles:
        ControleLevaItem.objects.create(
            leva=leva,
            controle_beneficio=controle,
            status='PENDENTE'
        )

    # 🔥 Marcar o primeiro como PROCESSANDO direto (opcional, se quiser iniciar assim)
    primeiro_item = leva.itens.order_by(
        'controle_beneficio__associado__user__first_name',
        'controle_beneficio__associado__user__last_name'
    ).first()

    if primeiro_item:
        primeiro_item.status = 'PROCESSANDO'
        primeiro_item.em_processamento_por = user
        primeiro_item.save()

    return leva

