from django.db import models
from django.conf import settings
from django.apps import apps
from datetime import date
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
import os

from django.contrib.auth.models import User
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Configuração para autenticar via service account
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'credentials.json')  # 🚨 Arquivo do Google

def upload_to_drive(file_path, file_name, folder_id):
    """Envia o arquivo para a pasta do Drive"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    media = MediaFileUpload(file_path, resumable=True)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file.get('id')



UF_CHOICES = [
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
    ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'),
    ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
    ('Não declarado', 'Não declarado'),
]

class BeneficioModel(models.Model):
    BENEFICIO_CHOICES = [
        ('seguro_defeso', 'Seguro Defeso'),
        ('seguro_tainha', 'Seguro Tainha'),
        ('seguro_camarao', 'Seguro Camarão')
        # pode crescer depois
    ]

    nome = models.CharField(max_length=80, choices=BENEFICIO_CHOICES)
    lei_federal = models.CharField(max_length=150, blank=True, null=True)
    instrucao_normativa = models.CharField(max_length=150, blank=True, null=True)
    portaria = models.CharField(max_length=150, blank=True, null=True)
    ano_concessao = models.PositiveIntegerField(default=date.today().year)
    estado = models.CharField(max_length=80, choices=UF_CHOICES)  # UF
    data_inicio = models.DateField()
    data_fim = models.DateField()
    anotacoes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('nome', 'ano_concessao', 'estado')
        verbose_name = "Benefício"
        verbose_name_plural = "Benefícios"
        
    def __str__(self):
        return f"{self.nome} - {self.ano_concessao}/{self.estado}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.criar_controles_para_associados()

    def criar_controles_para_associados(self):
        AssociadoModel = apps.get_model('app_associados', 'AssociadoModel')
        ControleModel = apps.get_model('app_beneficios', 'ControleBeneficioModel')

        associados = AssociadoModel.objects.filter(
            status='Associado Lista Ativo(a)',
            municipio_circunscricao__uf=self.estado  # ✅ só do mesmo estado do benefício
        )

        campo_por_beneficio = {
            'seguro_defeso': 'recebe_seguro',
            'seguro_tainha': 'recebe_tainha',
            'seguro_camarao': 'recebe_camarao',
        }

        campo_esperado = campo_por_beneficio.get(self.nome)

        if not campo_esperado:
            return

        for associado in associados:
            if hasattr(associado, campo_esperado):
                if getattr(associado, campo_esperado) == 'Recebe':
                    if not ControleModel.objects.filter(associado=associado, beneficio=self).exists():
                        ControleModel.objects.create(
                            associado=associado,
                            beneficio=self,
                            status_pedido='EM_PREPARO',
                        )



def protocolo_upload_path(instance, filename):
    # Normaliza nome do associado
    nome_slug = slugify(instance.associado.user.get_full_name(), allow_unicode=True)

    # Extrai tipo do benefício
    beneficio_tipo = instance.beneficio.nome.replace("seguro_", "").upper()
    ano = instance.beneficio.ano_concessao

    # Nome final do arquivo
    nome_arquivo = f"COMP_SEG_{beneficio_tipo}_{nome_slug}_{ano}.pdf"

    # Retorna caminho relativo para o FileField
    return os.path.join('comprovantes_beneficio', nome_arquivo)


class ControleBeneficioModel(models.Model):
    STATUS_CHOICES = [
        ('EM_PREPARO', 'Em Preparo'),
        ('PROTOCOLADO', 'Protocolado'),
        ('EXIGENCIA', 'Exigência'),
        ('EM_ANALISE', 'Em Análise'),
        ('RECURSO', 'Recurso'),
        ('INDEFERIDO', 'Indeferido'),
        ('DEFERIDO', 'Deferido'),
        ('ARQUIVADO', 'Arquivado'),
    ]
    associado = models.ForeignKey('app_associados.AssociadoModel', on_delete=models.CASCADE, related_name='beneficios')
    beneficio = models.ForeignKey(BeneficioModel, on_delete=models.CASCADE, related_name='controles')
    status_pedido = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EM_PREPARO')
    data_entrada = models.DateField(blank=True, null=True)
    numero_protocolo = models.CharField(max_length=50, blank=True, null=True)
    anotacoes_exigencias = models.TextField(blank=True, null=True)
    anotacoes_gerais = models.TextField(blank=True, null=True)
    resultado_final = models.TextField(blank=True, null=True)
    comprovante_protocolo = models.FileField(
        upload_to=protocolo_upload_path,
        blank=True,
        null=True,
        verbose_name="Comprovante do Protocolo"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('associado', 'beneficio')
        ordering = ['-data_entrada']
        verbose_name = "Controle de Benefício"
        verbose_name_plural = "Controle de Benefícios"

    def __str__(self):
        return f"{self.associado} - {self.beneficio.nome} ({self.status_pedido})"

    def save(self, *args, **kwargs):
        """
        Registra alterações no histórico ao salvar
        """
        if self.pk:  # Só se já existir no banco
            old = ControleBeneficioModel.objects.get(pk=self.pk)
            self.verificar_alteracoes(old)
        super().save(*args, **kwargs)
    
    def verificar_alteracoes(self, old_instance):
        """
        Compara e registra alterações nos campos monitorados
        """
        campos_monitorados = [
            'status_pedido',
            'data_entrada',
            'numero_protocolo',
            'comprovante_protocolo',
            'anotacoes_exigencias',
            'anotacoes_gerais',
            'resultado_final'
        ]
        
        user = getattr(self, '_current_user', None)
        
        for campo in campos_monitorados:
            valor_antigo = getattr(old_instance, campo)
            valor_novo = getattr(self, campo)
            
            if str(valor_antigo) != str(valor_novo):
                self.registrar_alteracao(campo, valor_antigo, valor_novo, user)
    
    def registrar_alteracao(self, campo, antigo, novo, user=None):
        """
        Cria um registro de histórico para uma alteração específica
        """
        # Tratamento especial para campos específicos
        if campo == 'status_pedido':
            antigo = dict(self.STATUS_CHOICES).get(antigo, antigo)
            novo = dict(self.STATUS_CHOICES).get(novo, novo)
        elif campo == 'comprovante_protocolo':
            antigo = getattr(antigo, 'name', '') if antigo else ''
            novo = getattr(novo, 'name', '') if novo else ''
        
        ControleBeneficioHistoricoModel.objects.create(
            controle=self,
            alterado_por=user,
            campo_alterado=self.get_label_campo(campo),
            valor_anterior=str(antigo)[:500],
            valor_novo=str(novo)[:500]
        )
    
    def get_label_campo(self, campo):
        """
        Retorna o nome amigável do campo
        """
        labels = {
            'status_pedido': 'Status do Pedido',
            'data_entrada': 'Data de Entrada',
            'numero_protocolo': 'Número do Protocolo',
            'comprovante_protocolo': 'Comprovante',
            'anotacoes_exigencias': 'Anotações de Exigências',
            'anotacoes_gerais': 'Anotações Gerais',
            'resultado_final': 'Resultado Final'
        }
        return labels.get(campo, campo.replace('_', ' ').title())
    
 
class ControleBeneficioHistoricoModel(models.Model):
    controle = models.ForeignKey('ControleBeneficioModel', on_delete=models.CASCADE, related_name='historico')
    alterado_em = models.DateTimeField(auto_now_add=True)
    alterado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    campo_alterado = models.CharField(max_length=50)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_novo = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-alterado_em']
        verbose_name = 'Histórico de Alteração'
        verbose_name_plural = 'Históricos de Alterações'

    def __str__(self):
        return f"{self.controle.associado} - {self.campo_alterado} em {self.alterado_em}"



# Processamento de Benefícios
class LevaProcessamentoBeneficio(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Descrição da Leva")
    beneficio = models.ForeignKey(
        BeneficioModel,
        on_delete=models.CASCADE,
        related_name="levas_processamento"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="levas_criadas"
    )
    encerrado = models.BooleanField(default=False, verbose_name="Leva Encerrada")

    def __str__(self):
        return f"Leva: {self.nome} - {self.beneficio} ({'Encerrada' if self.encerrado else 'Em andamento'})"
    
    
class ControleLevaItem(models.Model):
    leva = models.ForeignKey(
        LevaProcessamentoBeneficio,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    controle_beneficio = models.ForeignKey(
        ControleBeneficioModel,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[('PENDENTE', 'Pendente'), ('PROCESSANDO', 'Processando'), ('CONCLUIDO', 'Concluído')],
        default='PENDENTE'
    )
    em_processamento_por = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='processando_itens'
    )
    atualizado_por = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='atualizou_itens'
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.status != 'PROCESSANDO':
            self.em_processamento_por = None
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.leva} - {self.controle_beneficio}"
