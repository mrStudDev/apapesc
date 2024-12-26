from django.db import models
from django.contrib.auth.models import User


PRIORIDADES_TAREFA = [
    ('alta', 'Alta'),
    ('media', 'Média'),
    ('baixa', 'Baixa'),
]

STATUS_TAREFA = [
    ('pendente', 'Pendente'),
    ('em_andamento', 'Em Andamento'),
    ('concluida', 'Concluída'),
    ('devolvida', 'Devolvida'),
    ('arquivada', 'Arquivada'),
    ('desarquivada', 'Desarquivada'),
]

CATEGORIAS_TAREFA = [
    ('administrativa', 'Administrativa'),
    ('associado', 'Associado'),
    ('integrante', 'Integrante'),
    ('outro', 'Outro'),
]

# Create your models here.
class TarefaModel(models.Model):

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
    status = models.CharField(
        max_length=20, 
        choices=STATUS_TAREFA, 
        default='aberta',
        verbose_name="status da Tarefa"
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
    criado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tarefas_criadas',
        verbose_name="Criado por"
        )
    associado = models.ForeignKey(
        'app_associados.AssociadoModel', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Associado"
    )
    responsaveis = models.ManyToManyField(
        'app_associacao.IntegrantesModel',
        related_name='tarefas_atribuidas',
        verbose_name="Responsáveis"
        )
    content = models.TextField(
        null=True, blank=True,
        verbose_name="Anotações"
    )

    def __str__(self):
        return self.titulo