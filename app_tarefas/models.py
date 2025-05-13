from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils.timezone import now, timezone
from django.utils.text import slugify
from decimal import Decimal
from django.db import transaction
    
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
# Registro de lote para um mês e ano específicos
class LancamentoINSSModel(models.Model):
    ano = models.PositiveIntegerField(verbose_name="Ano de Referência")
    
    MESES_VALIDOS = [(i, f'{i:02d}') for i in range(4, 12)]  # abril (4) até novembro (11)
    mes = models.PositiveIntegerField(
        choices=MESES_VALIDOS,
        verbose_name="Mês de Referência"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='lancamentos_inss',
        verbose_name="Criado por"
    )
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('ano', 'mes')
        ordering = ['-ano', '-mes']
        verbose_name = "Lançamento INSS"
        verbose_name_plural = "Lançamentos INSS"

    def __str__(self):
        return f"INSS {self.mes:02d}/{self.ano}"


    @classmethod
    @transaction.atomic
    def gerar_lancamento(cls, ano, mes, user):
        print(f"🔁 Gerando lançamento para {mes:02d}/{ano}")
        
        lancamento, created = cls.objects.get_or_create(
            ano=ano,
            mes=mes,
            defaults={'criado_por': user}
        )

        # 🔍 Somente associados com recolhe_inss="Sim" E que estão ativos
        associados = AssociadoModel.objects.filter(
            recolhe_inss="Sim",
            status="Associado Lista Ativo(a)"
        )
        print(f"🔎 Associados ativos que recolhem INSS: {associados.count()}")

        guias_criadas = 0
        for associado in associados:
            exists = GuiaINSSModel.objects.filter(
                lancamento=lancamento,
                associado=associado
            ).exists()
            print(f"➡️ Associado {associado.id} | Guia existe? {exists}")
            
            if not exists:
                GuiaINSSModel.objects.create(
                    lancamento=lancamento,
                    associado=associado,
                    status='pendente'
                )
                guias_criadas += 1
                print(f"✅ Criada guia para {associado}")

        print(f"📦 Total guias criadas: {guias_criadas}")
        return lancamento, created, guias_criadas


    
# Registro individual para cada associado no lançamento
class GuiaINSSModel(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('emitida', 'Emitida'),
        ('paga', 'Paga'),
        ('atrasada', 'Atrasada'),
    ]

    OBSERVACOES_CHOICES = [
        ('validar_acesso', 'Validar Acesso'),
        ('senha_invalida', 'Senha Inválida'),
        ('nivel_conta', 'Nível Conta'),
        ('sem_login', 'Sem Login'),
        ('sem_caepf', 'Sem CAEPF'),
        ('certo', 'Certo')
    ]

    lancamento = models.ForeignKey(
        LancamentoINSSModel, 
        on_delete=models.CASCADE,
        related_name='guias',
        verbose_name="Lançamento",
        null=True
    )
    associado = models.ForeignKey(
        'app_associados.AssociadoModel',
        on_delete=models.CASCADE,
        related_name='guias_inss',
        verbose_name="Associado"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    observacoes = models.CharField(
        max_length=50,
        choices=OBSERVACOES_CHOICES,  # ✅ agora usa o atributo correto
        default='certo',
        null=True,
        blank=True
    )

    data_emissao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lancamento', 'associado')
        verbose_name = "Guia de INSS"
        verbose_name_plural = "Guias de INSS"

    def __str__(self):
        return f"{self.associado} - {self.lancamento}"

    @staticmethod
    def get_status_choices():
        return GuiaINSSModel.STATUS_CHOICES

    @staticmethod
    def get_observacoes_choices():
        return GuiaINSSModel.OBSERVACOES_CHOICES

# models.py
class ProgressoGuiaINSSModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lancamento = models.ForeignKey(LancamentoINSSModel, on_delete=models.CASCADE)
    ultima_guia = models.ForeignKey(GuiaINSSModel, on_delete=models.CASCADE)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lancamento')
