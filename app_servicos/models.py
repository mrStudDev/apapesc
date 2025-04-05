from django.db import models
from app_associados.models import AssociadoModel
from app_finances.models import TipoServicoModel, EntradaFinanceira
from app_associacao.models import AssociacaoModel, ReparticoesModel

from decimal import Decimal
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class StatusEtapaChoices(models.TextChoices):
    # Comum
    PENDENTE = "pendente", "Pendente"
    ARQUIVADO = "arquivado", "Arquivado"

    # Documento
    DOC_PROTOCOLADO = "doc_protocolado", "Documento Protocolado"
    DOC_EXIGENCIA = "doc_exigencia", "Documento em Exigência"
    DOC_ANALISE = "doc_analise", "Documento em Análise"
    DOC_RECURSO = "doc_recurso", "Documento em Recurso"
    DOC_DEFERIDO = "doc_deferido", "Documento Deferido"
    DOC_INDEFERIDO = "doc_indeferido", "Documento Indeferido"

    # Serviço
    SERVICO_ANDAMENTO = "servico_andamento", "Serviço em Andamento"
    SERVICO_CONCLUIDO = "servico_concluido", "Serviço Concluído"
    SERVICO_ESPERA = "servico_espera", "Serviço em Espera"


# Serviço associado
class ServicoAssociadoModel(models.Model):
    NATUREZA_CHOICES = [
        ('emissao_documento', 'Emissão de Documento'),
        ('servico_consultoria', 'Serviço de Consultoria'),
        ('servico_geral', 'Serviço Geral'),

    ]
    natureza_servico = models.CharField(
        max_length=50,
        choices=NATUREZA_CHOICES,
        verbose_name="Natureza do Serviço"
    )          
    # Vínculo
    associacao = models.ForeignKey(
        AssociacaoModel, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True, 
        related_name='servicos_associacao',
        verbose_name="Associação"
    )
    reparticao = models.ForeignKey(
        ReparticoesModel, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True, 
        related_name='servicos_reparticao',
        verbose_name="Repartição"
    )    

    tipo_servico = models.ForeignKey(TipoServicoModel, on_delete=models.SET_NULL, null=True)

    # 🔹 Só um desses será preenchido
    associado = models.ForeignKey(
        AssociadoModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Associado"
    )

    data_inicio = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, null=True)
    
    status_etapa = models.CharField(
        max_length=20,
        choices=StatusEtapaChoices.choices,
        default=StatusEtapaChoices.PENDENTE
    )

    ultima_alteracao = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='servicos_criados')
      

    def __str__(self):
        return f"{self.associado} - {self.tipo_servico}"


# Serviço EXTRA-ASSOCIADO
class ServicoExtraAssociadoModel(models.Model):
    NATUREZA_CHOICES = [
        ('emissao_documento', 'Emissão de Documento'),
        ('servico_consultoria', 'Serviço de Consultoria'),
        ('servico_geral', 'Serviço Geral'),

    ]
    natureza_servico = models.CharField(
        max_length=50,
        choices=NATUREZA_CHOICES,
        verbose_name="Natureza do Serviço"
    )      
    # Vínculo
    associacao = models.ForeignKey(
        AssociacaoModel, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True, 
        related_name='servicos_extra_associacao',
        verbose_name="Associação"
    )
    reparticao = models.ForeignKey(
        ReparticoesModel, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True, 
        related_name='servicos_extra_reparticao',
        verbose_name="Repartição"
    )
    extra_associado = models.ForeignKey(
        'ExtraAssociadoModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Extra Associado"
    )

    tipo_servico = models.ForeignKey(TipoServicoModel, on_delete=models.SET_NULL, null=True)

    data_inicio = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, null=True)
    
    status_etapa = models.CharField(
        max_length=20,
        choices=StatusEtapaChoices.choices,
        default=StatusEtapaChoices.PENDENTE
    )

    ultima_alteracao = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        User, 
        null=True, blank=True, 
        on_delete=models.SET_NULL, 
        related_name='servicos_extra_associados'
        )
    
    entrada_relacionada = models.OneToOneField(
        'app_finances.EntradaFinanceira',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entrada_servico_extra',  # 💡 ALTERADO AQUI!
        verbose_name="Entrada Financeira Relacionada"
    )

    
    def __str__(self):
        return f"{self.extra_associado} - {self.tipo_servico}"
      


class ServicoHistoricoModel(models.Model):
    servico_associado = models.ForeignKey(
        ServicoAssociadoModel,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name="Serviço Associado",
        default=None,
        blank=True,
        null=True
    )
    servico_extra_associado = models.ForeignKey(
        ServicoExtraAssociadoModel,
        on_delete=models.CASCADE,
        related_name='historico_extra',
        blank=True,
        null=True
    )
    campo = models.CharField(max_length=100, verbose_name="Campo Alterado")
    valor_antigo = models.TextField(blank=True, null=True)
    valor_novo = models.TextField(blank=True, null=True)
    alterado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        ordering = ['-data_alteracao']
        verbose_name = "Histórico do Serviço"
        verbose_name_plural = "Histórico dos Serviços"

    def __str__(self):
        return f"{self.campo} alterado por {self.alterado_por} em {self.data_alteracao.strftime('%d/%m/%Y %H:%M')}"
    
    
    
    
class ExtraAssociadoModel(models.Model):
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(
        max_length=14,
        unique=True,
        verbose_name="CPF"
    )
    senha_gov = models.CharField(
        max_length=128, 
        blank=True, 
        null=True,
        help_text="Senha criptografada para segurança."
    )
    celular = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                r'^\(\d{2}\)\d{5}-\d{4}$',  # Garante que o número seja no formato (XX)XXXXX-XXXX
                'Número inválido. O telefone deve conter 10 ou 11 dígitos, ex: (48)99999-9999.'
            )
        ]
    )  
    content = models.TextField()


    def __str__(self):
        return self.nome_completo

    @property
    def servicos(self):
        return self.servicoextraassociadomodel_set.all()      