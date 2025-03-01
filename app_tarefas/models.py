from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify

from django.contrib.auth import get_user_model
from app_associados.models import AssociadoModel

User = get_user_model()

PRIORIDADES_TAREFA = [
    ('alta', 'Alta'),
    ('media', 'Média'),
    ('baixa', 'Baixa'),
]


CATEGORIAS_TAREFA = [
    ('administrativa', 'Administrativa'),
    ('associado', 'Associado'),
    ('integrante', 'Integrante'),
    ('sistema', 'Sistema'),
    ('outro', 'Outro'),
]

# Create your models here.
class TarefaModel(models.Model):
    STATUS_TAREFA = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('devolvida', 'Devolvida'),
        ('arquivada', 'Arquivada'),
        ('desarquivada', 'Desarquivada'),
    ]
    criado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tarefas_criadas',
        verbose_name="Criado por"
    )
    titulo = models.CharField(max_length=255)
    descricao = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Breve Descrição"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_conclusao = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Data Conlusão"
    )
    data_limite = models.DateField(
        blank=True, null=True
    )
    hora_limite = models.TimeField(
        blank=True, null=True
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_TAREFA, 
        verbose_name="status da Tarefa", 
        default='pendente'
    )
    categoria = models.CharField(
        max_length=20, 
        choices=CATEGORIAS_TAREFA, 
        default='outro',
        verbose_name="Categoria"
    )
    prioridade = models.CharField(
        max_length=20, 
        choices=PRIORIDADES_TAREFA, 
        default='media',
        verbose_name="Prioridade"
    )
    responsaveis = models.ManyToManyField(
        'app_associacao.IntegrantesModel',
        related_name='tarefas_atribuidas',
        verbose_name="Responsáveis"
    )    
    associado = models.ForeignKey(
        'app_associados.AssociadoModel', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Associado"
    )

    content = models.TextField(
        null=True, blank=True,
        verbose_name="Anotações"
    )
    arquivada = models.BooleanField(default=False, verbose_name="Arquivada")

    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titulo)
            slug = base_slug
            counter = 1

            while TarefaModel.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
# ===================== End Tarefa


# Histórico Status
class HistoricoStatusModel(models.Model):
    tarefa = models.ForeignKey(
        'app_tarefas.TarefaModel',
        on_delete=models.CASCADE,
        related_name='historico_status',
        verbose_name="Tarefa"
    )
    status_anterior = models.CharField(max_length=50, verbose_name="Status Anterior")
    status_novo = models.CharField(max_length=50, verbose_name="Status Novo")
    alterado_por = models.ForeignKey(
        'app_associacao.IntegrantesModel',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Alterado por"
    )
    data_alteracao = models.DateTimeField(default=now, verbose_name="Data de Alteração")

    def __str__(self):
        return f"{self.tarefa} - {self.status_anterior} → {self.status_novo}"
# ===================== End Satatus

# Histórico Responsáveis 
class HistoricoResponsaveisModel(models.Model):
    tarefa = models.ForeignKey(
        'app_tarefas.TarefaModel',
        on_delete=models.CASCADE,
        related_name='historico_responsaveis',
        verbose_name="Tarefa"
    )
    responsaveis_anteriores = models.ManyToManyField(
        'app_associacao.IntegrantesModel',
        related_name='responsaveis_anteriores',
        verbose_name="Responsáveis Anteriores"
    )
    responsaveis_novos = models.ManyToManyField(
        'app_associacao.IntegrantesModel',
        related_name='responsaveis_novos',
        verbose_name="Responsáveis Novos"
    )
    alterado_por = models.ForeignKey(
        'app_associacao.IntegrantesModel',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Alterado por"
    )
    data_alteracao = models.DateTimeField(default=now, verbose_name="Data de Alteração")

    def __str__(self):
        return f"{self.tarefa} - Responsáveis alterados"
# ===================== End Responsáveis


# ======== INSS ==========

MESES_GUIAS = [
    (4, "Abril"), (5, "Maio"), (6, "Junho"), (7, "Julho"),
    (8, "Agosto"), (9, "Setembro"), (10, "Outubro"), (11, "Novembro")
]

class GuiaINSSModel(models.Model):
    associado = models.ForeignKey(
        AssociadoModel, 
        on_delete=models.CASCADE, 
        related_name="guias_inss",
        verbose_name="Associado"
    )
    mes_referencia = models.PositiveSmallIntegerField(choices=MESES_GUIAS, verbose_name="Mês de Referência")
    ano = models.PositiveIntegerField(default=now().year, verbose_name="Ano")
    data_emissao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Emissão")
    emitido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Emitido por")

    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("emitido", "Emitido"),
        ("enviado", "Enviado")
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pendente", verbose_name="Status")

    class Meta:
        ordering = ["ano", "mes_referencia"]
        verbose_name = "Guia INSS"
        verbose_name_plural = "Guias INSS"

    def __str__(self):
        return f"{self.get_mes_referencia_display()} - {self.ano} | {self.associado}"


