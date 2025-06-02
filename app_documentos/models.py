from django.db import models
from django.utils import timezone
from app_associados.models import AssociadoModel
from app_tarefas.models import TarefaModel
from app_servicos.models import ExtraAssociadoModel
from datetime import datetime
from django.core.exceptions import ValidationError

class TipoDocumentoModel(models.Model):
    tipo = models.CharField(
        max_length=1500,
        unique=True,
        verbose_name="Nome do Tipo de Documento"
    )
    descricao = models.TextField(null=True, blank=True)

    def clean(self):
        # Confere se já existe um "tipo" igual (case-insensitive), ignorando ele mesmo
        if TipoDocumentoModel.objects.filter(tipo__iexact=self.tipo).exclude(pk=self.pk).exists():
            raise ValidationError({'tipo': 'Este tipo de documento já está cadastrado.'})

    def __str__(self):
        return self.tipo


class Documento(models.Model):
    associado = models.ForeignKey(
        'app_associados.AssociadoModel',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='documentos'
    )
    integrante = models.ForeignKey(
        'app_associacao.IntegrantesModel',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='documentos'
    )
    associacao = models.ForeignKey(
        'app_associacao.AssociacaoModel',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='associacao_documentos'
    )
    reparticao = models.ForeignKey(
        'app_associacao.ReparticoesModel',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='reparticao_documentos'
    )
    tarefa = models.ForeignKey(
        'app_tarefas.TarefaModel',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='tarefa_documentos'        
    )
    extra_associado = models.ForeignKey(
        'app_servicos.ExtraAssociadoModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documentos'
    )
    embarcacao = models.ForeignKey(
        'app_embarcacoes.EmbarcacoesModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documentos'
    )    
    tipo_doc = models.ForeignKey(
        'TipoDocumentoModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Documento"
    )
    nome = models.CharField(max_length=1500, verbose_name="Nome do Documento", blank=True)
    arquivo = models.FileField(upload_to='documentos/', verbose_name="Arquivo", max_length=1500)
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")

    def save(self, *args, **kwargs):
        # Inicializa a data atual formatada
        data_str = timezone.now().strftime('%Y-%m-%d')

        # Determina o proprietário (associado, integrante ou associação) e usa nome e sobrenome
        if self.associado:
            nome_proprietario = f"{self.associado.user.first_name} {self.associado.user.last_name}"
        elif self.integrante:
            nome_proprietario = f"{self.integrante.user.first_name} {self.integrante.user.last_name}"
        elif self.associacao:
            nome_proprietario = self.associacao.nome_fantasia
        elif self.reparticao:
            nome_proprietario = self.reparticao.nome_reparticao
        elif self.tarefa:
            nome_proprietario = self.tarefa.titulo
        elif self.extra_associado:
            nome_proprietario = f"{self.extra_associado.nome_completo}"
        elif self.embarcacao:
            nome_proprietario = f"{self.embarcacao.nome_embarcacao}"
        else:
            raise ValueError("Documento deve estar associado a um Associado, Tarefa, ExtraAssociado, Integrante ou Associação.")

        # Define o nome do documento
        if self.tipo_doc:
            nome_documento = f"{self.tipo_doc.tipo} - {nome_proprietario} - {data_str}"
        elif self.nome:  # Usa o nome fornecido se não houver tipo_doc
            nome_documento = f"{self.nome} - {nome_proprietario} - {data_str}"
        else:
            # Define um nome padrão caso nenhum tipo ou nome sejam fornecidos
            nome_documento = f"Documento sem tipo - {nome_proprietario} - {data_str}"

        # Trunca o nome do documento se exceder 1500 caracteres
        self.nome = nome_documento[:1500]

        super().save(*args, **kwargs)


    def __str__(self):
        if self.associado:
            return f"{self.nome} - Associado: {self.associado.user.first_name} {self.associado.user.last_name}"
        elif self.integrante:
            return f"{self.nome} - Integrante: {self.integrante.user.first_name} {self.integrante.user.last_name}"
        elif self.associacao:
            return f"{self.nome} - Associacao: {self.associacao.nome_fantasia}"
        elif self.reparticao:
            return f"{self.nome} - Repartição: {self.reparticao.nome_reparticao}"
        elif self.tarefa:
            return f"{self.nome} - Tarefa: {self.tarefa.titulo}"
        elif self.extra_associado:
            return f"{self.nome} - Extra Associado: {self.extra_associado.nome_completo}"
        elif self.embarcacao:
            return f"{self.nome} - Embarcação: {self.embarcacao.nome_embarcacao}"
        else:
            return f"{self.nome} - Sem proprietário definido"



# UPLOADS TO DRIVE ASSOCIADOS FOLDER
# app_documentos/models.py

class UpDocDriveModel(models.Model):
    associado = models.ForeignKey(AssociadoModel, on_delete=models.CASCADE, related_name='upload_drivefolder')
    tipo_documento = models.ForeignKey('TipoDocumentoModel', on_delete=models.PROTECT)
    arquivo = models.FileField(upload_to='temp_docs/')  # Pasta temporária
    nome_final = models.CharField(max_length=500, blank=True)
    data_envio = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.nome_final:
            self.nome_final = f"{self.tipo_documento.tipo} - {self.associado.user.get_full_name()} - {datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        super().save(*args, **kwargs)
