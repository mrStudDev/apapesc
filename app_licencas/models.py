# app_licencas/models.py
from django.db import models
from app_embarcacoes.models import EmbarcacoesModel
from django.utils.timezone import now
from datetime import timedelta, date



class LicencasModel(models.Model):
    ORGAO_CHOICES = [
        ('MAPA', 'Ministério da Agricultura, Pecuária e Abastecimento'),
        ('IBAMA', 'IBAMA'),
        ('MMA', 'Ministério do Meio Ambiente'),
        ('SPU', 'Secretaria do Patrimônio da União'),
        # adicione mais se necessário
    ]

    LICENCA_CHOICES = [
        ('registro_embarcacao', 'Certificado de Registro e Autorização de Embarcação Pesqueira'),
        ('licenca_ambiental', 'Licença Ambiental'),
        ('outorga', 'Outorga de Uso de Recursos Hídricos'),
        # adicione mais
    ]

    embarcacao = models.ForeignKey(
        'app_embarcacoes.EmbarcacoesModel',
        on_delete=models.CASCADE,
        related_name='licencas'  # 👈 importante!
    )
    
    orgao_nome = models.CharField(max_length=50, choices=ORGAO_CHOICES)
    licenca_nome = models.CharField(max_length=50, choices=LICENCA_CHOICES)

    num_processo = models.CharField(max_length=100, verbose_name="Nº Processo", blank=True, null=True)
    num_atoAdmConcede = models.CharField(max_length=100, verbose_name="Nº Ato Administrativo", blank=True, null=True)
    codigo_frota = models.CharField(max_length=50, blank=True, null=True)
    inscricao_aut_naval = models.CharField(max_length=100, blank=True, null=True)

    modalidade_permissionamento = models.TextField(blank=True, null=True)

    validade_inicial = models.DateField()
    validade_final = models.DateField()
    data_alteracao = models.DateTimeField(auto_now=True)

    content = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Licença de Embarcação"
        verbose_name_plural = "Licenças de Embarcações"
        

    def __str__(self):
        return f"{self.get_licenca_nome_display()} - {self.embarcacao.nome_embarcacao}"

    @property
    def associado(self):
        return self.embarcacao.proprietario
    
    @property
    def status_validade(self):
        if not self.validade_final:
            return 'sem_licenca'
        hoje = date.today()
        if self.validade_final < hoje:
            return 'vencida'
        elif self.validade_final <= hoje + timedelta(days=30):
            return 'alerta'
        return 'ok'

    @property
    def dias_para_vencimento(self):
        if self.validade_final:
            return (self.validade_final - date.today()).days
        return 0  # ou -999 como código de erro, mas 0 é seguro pra exibir

