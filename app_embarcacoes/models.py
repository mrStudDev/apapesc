# app_embarcacoes/models.py

from django.db import models
from django.contrib.auth.models import User
from app_associados.models import AssociadoModel
from datetime import date, timedelta

class TipoEmbarcacaoModel(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class TipoPropulsaoModel(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class EmbarcacoesModel(models.Model):

    COMBUSTIVEL_CHOICES = [
        ('gasolina', 'Gasolina'),
        ('alcool', 'Álcool'),
        ('diesel', 'Diesel'),
        ('gas', 'Gás'),

    ]

    ALIENACAO_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
    ]
    
    PORTE_EMBARCACAO = [
        ('miuda', 'Miuda'),
        ('maior porte', 'Maior Porte')        
    ]
    
    SEGURO_DPEM_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
    ]

    proprietario = models.ForeignKey(
        AssociadoModel,
        on_delete=models.CASCADE,
        related_name='embarcacoes',
        verbose_name='Proprietário'
    )

    destaque_embarcacao_img = models.ImageField(
        upload_to='embarcacoes/destaques/',
        blank=True,
        null=True,
        verbose_name='Imagem em destaque da embarcação'
    )

    nome_embarcacao = models.CharField(max_length=100)    
    inscricao_embarcacao = models.CharField(max_length=100, unique=True)

    tipo_embarcacao = models.ForeignKey(
        TipoEmbarcacaoModel,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Tipo de Embarcação"
    )

    validade_tie = models.DateField(verbose_name='Validade TIE')

    atividade = models.CharField(max_length=100)
    area_navegacao = models.CharField(max_length=100)

    numero_tripulantes = models.PositiveIntegerField()
    numero_passageiros = models.PositiveIntegerField()

    porte = models.CharField(
        max_length=25, choices=PORTE_EMBARCACAO, default=None
    )
    cumprimento = models.DecimalField(max_digits=6, decimal_places=2)
    ab_gt = models.CharField(max_length=100, blank=True, null=True)
    boca = models.CharField(max_length=100, blank=True, null=True)

    tipo_propulsao = models.ForeignKey(
        TipoPropulsaoModel,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Tipo de Propulsão"
    )

    combustivel = models.CharField(
        max_length=15, choices=COMBUSTIVEL_CHOICES
    )

    motor_1 = models.CharField(max_length=100, blank=True, null=True)
    numero_serie_1 = models.CharField(max_length=100, blank=True, null=True)
    potencia_hp1 = models.CharField(max_length=100, blank=True, null=True)
    
    motor_2 = models.CharField(max_length=100, blank=True, null=True)
    numero_serie_2 = models.CharField(max_length=100, blank=True, null=True)
    potencia_hp2 = models.CharField(max_length=100, blank=True, null=True)

    motor_3 = models.CharField(max_length=100, blank=True, null=True)
    numero_serie_3 = models.CharField(max_length=100, blank=True, null=True)
    potencia_hp3 = models.CharField(max_length=100, blank=True, null=True)

    motor_4 = models.CharField(max_length=100, blank=True, null=True)
    numero_serie_4 = models.CharField(max_length=100, blank=True, null=True)
    potencia_hp4 = models.CharField(max_length=100, blank=True, null=True)
    
    ano_construcao = models.DateField(blank=True, null=True)
    construtor_nome = models.CharField(max_length=100, blank=True, null=True)
    material_construcao = models.CharField(max_length=100, blank=True, null=True)
    arqueacao_bruta = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    alienacao = models.CharField(
        max_length=5, choices=ALIENACAO_CHOICES, default='nao'
    )


    co_proprietario_nome = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Co-Proprietário'
    )
    
    municipio_emissao = models.CharField(max_length=100)
    data_emissao = models.DateField()
    data_atualizacao = models.DateField(auto_now=True)


    traves_img = models.ImageField(
        upload_to='embarcacoes/traves/',
        blank=True,
        null=True,
        verbose_name='Imagem da Trave (lado da embarcação)'
    )

    popa_img = models.ImageField(
        upload_to='embarcacoes/popa/',
        blank=True,
        null=True,
        verbose_name='Imagem da Popa'
    )
    seguro_dpen = models.CharField(
        max_length=5, choices=SEGURO_DPEM_CHOICES, default='nao'
    )
    seguro_dpem_numero = models.CharField(max_length=100, blank=True, null=True)
    seguro_dpem_data_vencimento = models.DateField(blank=True, null=True)
    
    content = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.nome_embarcacao} ({self.inscricao_embarcacao})"

    @property
    def status_validade(self):
        hoje = date.today()
        licencas = self.licencas.all()

        if not licencas.exists():
            return 'sem_licenca'

        status_list = []
        for licenca in licencas:
            if licenca.validade_final:
                if licenca.validade_final < hoje:
                    status_list.append('vencida')
                elif licenca.validade_final <= hoje + timedelta(days=30):
                    status_list.append('alerta')
                else:
                    status_list.append('ok')

        if 'alerta' in status_list:
            return 'alerta'
        elif 'vencida' in status_list and 'ok' not in status_list:
            return 'vencida'
        elif 'ok' in status_list:
            return 'ok'
        return 'sem_licenca'

    @property
    def licenca_mais_recente(self):
        return self.licencas.order_by('-validade_final').first()

    @property
    def dias_para_vencimento(self):
        licenca = self.licenca_mais_recente
        if licenca and licenca.validade_final:
            return (licenca.validade_final - date.today()).days
        return None

    @property
    def data_validade_mais_recente(self):
        licenca = self.licenca_mais_recente
        if licenca and licenca.validade_final:
            return licenca.validade_final
        return None


    @property
    def status_tie(self):
        if not self.validade_tie:
            return 'sem_validade'
        
        hoje = date.today()
        if self.validade_tie < hoje:
            return 'vencida'
        elif self.validade_tie <= hoje + timedelta(days=30):
            return 'alerta'
        return 'ok'

    @property
    def dias_para_vencimento_tie(self):
        if self.validade_tie:
            return (self.validade_tie - date.today()).days
        return None    

    @property
    def dias_para_vencimento_tie_abs(self):
        if self.dias_para_vencimento_tie is not None:
            return abs(self.dias_para_vencimento_tie)
        return None

    @property
    def dpem_dias_para_vencimento(self):
        if self.seguro_dpem_data_vencimento:
            return (self.seguro_dpem_data_vencimento - date.today()).days
        return None

    @property
    def status_dpem(self):
        dias = self.dpem_dias_para_vencimento
        if dias is None:
            return None
        if dias < 0:
            return 'vencida'
        elif dias <= 30:
            return 'alerta'
        else:
            return 'ok'