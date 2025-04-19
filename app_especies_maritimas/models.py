from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from django.utils.text import slugify
import random



class ReinoModel(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
       
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)    
            
    def __str__(self):
        return self.nome
    

class FiloModel(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    reino = models.ForeignKey(ReinoModel, on_delete=models.CASCADE)
    descricao = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
       
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)       
    
    def __str__(self):
        return self.nome

class GrupoBiologicoModel(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
       
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.nome

class HabitatModel(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)


CLASSE_CHOICES = [
    ('actinopterygii', 'Actinopterygii (Peixes ósseos)'),
    ('chondrichthyes', 'Chondrichthyes (Peixes cartilaginosos)'),
    ('malacostraca', 'Malacostraca (Crustáceos)'),
    # Adicione outras classes relevantes
]

ORDEM_CHOICES = [
    ('perciformes', 'Perciformes'),
    ('decapoda', 'Decapoda'),
    ('cetacea', 'Cetacea'),
    # Adicione outras ordens relevantes
]

FAMILIA_CHOICES = [
    ('serranidae', 'Serranidae (Garoupas)'),
    ('penaeidae', 'Penaeidae (Camarões peneídeos)'),
    ('delphinidae', 'Delphinidae (Golfinhos)'),
    # Adicione outras famílias relevantes
]

class EspecieMarinhaModel(models.Model):
    nome_comum = models.CharField(max_length=100, verbose_name="Nome Comum")  
    nome_cientifico = models.CharField(max_length=150, verbose_name="Nome Científico", unique=True)
    
    imagem_principal = models.ImageField(
    upload_to='especies/',
    blank=True,
    null=True,
    verbose_name="Imagem representativa",
    help_text="Imagem principal da espécie"
    )
    
    reino = models.ForeignKey(ReinoModel, on_delete=models.SET_NULL, null=True, blank=True)
    filo = models.ForeignKey(FiloModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    grupo_biologico = models.ForeignKey(GrupoBiologicoModel, on_delete=models.SET_NULL, null=True, blank=True)
    
    classe = models.CharField(
        max_length=100,
        choices=CLASSE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Classe Taxonômica"
    )
    ordem = models.CharField(
        max_length=100,
        choices=ORDEM_CHOICES,
        blank=True,
        null=True,
        verbose_name="Ordem Taxonômica"
    )
    familia = models.CharField(
        max_length=100,
        choices=FAMILIA_CHOICES,
        blank=True,
        null=True,
        verbose_name="Família Taxonômica",
    )

    # Melhorar campos existentes
    habitat = models.ManyToManyField(HabitatModel, blank=True)
    profundidade_minima = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    profundidade_maxima = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    temperatura_minima = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperatura_maxima = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Adicionar campos de controle
    validado = models.BooleanField(default=False)
    especialista_validacao = models.CharField(max_length=100, blank=True, null=True)
    data_validacao = models.DateField(null=True, blank=True)
    
    # Relação com espécies similares/relacionadas
    especies_relacionadas = models.ManyToManyField('self', blank=True)
    
    # Métricas de tamanho
    tamanho_medio = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Tamanho médio (cm)",
        help_text="Comprimento médio em centímetros"
    )
    tamanho_maximo = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Tamanho máximo (cm)",
        help_text="Comprimento máximoo em centímetros"
    )
    
    importancia_economica = models.BooleanField(default=False, verbose_name="Importância Econômica")
    permitida_pesca = models.BooleanField(default=True, verbose_name="Permitida para Pesca")

    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição Geral")
    comportamento = models.TextField(blank=True, null=True, verbose_name="Comportamento e Alimentação")
    epoca_reproducao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Época de Reprodução")

    fonte_pesquisa = models.CharField(max_length=255, blank=True, null=True, verbose_name="Fonte da Informação")
    link_referencia = models.URLField(blank=True, null=True, verbose_name="Link da Referência")
    data_cadastro = models.DateField(auto_now_add=True)
    data_ultima_alteracao = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

    code = models.PositiveIntegerField(unique=True, blank=True, null=True)

    
    def generate_unique_code(self):
        code = random.randint(100000, 999999)
        while EspecieMarinhaModel.objects.filter(code=code).exists():
            code = random.randint(100000, 999999)
        return code

    def save(self, *args, **kwargs):
        # Gera o código único se ainda não houver
        if not self.code:
            self.code = self.generate_unique_code()

        # Gera o slug a partir do nome (ou title se quiser usar outro campo)
        if not self.slug:
            self.slug = slugify(self.nome_comum)

        # Chama o save original do Django
        super().save(*args, **kwargs)

        
            
    class Meta:
        get_latest_by = "data_ultima_alteracao"
        ordering = ['nome_cientifico']
        indexes = [
            models.Index(fields=['nome_cientifico']),
            models.Index(fields=['nome_comum']),
        ]

    def clean(self):
        if self.profundidade_minima and self.profundidade_maxima and self.profundidade_minima > self.profundidade_maxima:
            raise ValidationError({'profundidade_minima': 'Não pode ser maior que a profundidade máxima'})
        
        if self.temperatura_minima and self.temperatura_maxima and self.temperatura_minima > self.temperatura_maxima:
            raise ValidationError({'temperatura_minima': 'Não pode ser maior que a temperatura máxima'})
            

class ReferenciaBibliograficaModel(models.Model):
    especie = models.ForeignKey(EspecieMarinhaModel, on_delete=models.CASCADE, related_name='referencias_bibliograficas')
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    ano = models.PositiveIntegerField()
    link = models.URLField(blank=True)
    
    
class RegiaoGeograficaModel(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)


# Distrinuição Geográfica
class DistribuicaoGeograficaModel(models.Model):
    especie = models.ForeignKey(EspecieMarinhaModel, on_delete=models.CASCADE, related_name='distribuicao_geografica')
    regiao = models.ForeignKey(RegiaoGeograficaModel, on_delete=models.SET_NULL, null=True, blank=True)
    detalhes = models.CharField(max_length=100, blank=True, null=True)
    
    def get_distribuicoes(self):
        return ", ".join([d.get_regiao_display() for d in self.distribuicaogeografica_set.all()])
    
# Status de conservação 
STATUS_IUCNABR = [
    ('LC', 'Pouco Preocupante (LC - Least Concern)'),
    ('NT', 'Quase Ameaçado (NT - Near Threatened)'),
    ('VU', 'Vulnerável (VU - Vulnerable)'),
    ('EN', 'Em Perigo (EN - Endangered)'),
    ('CR', 'Criticamente Ameaçado (CR - Critically Endangered)'),
    ('EW', 'Extinto na Natureza (EW - Extinct in the Wild)'),
    ('EX', 'Extinto (EX - Extinct)'),
    ('DD', 'Dados Deficientes (DD - Data Deficient)'),
    ('NE', 'Não Avaliado (NE - Not Evaluated)'),
]

class StatusConservacaoModel(models.Model):
    especie = models.ForeignKey(EspecieMarinhaModel, on_delete=models.CASCADE, related_name="status_conservacao")
    sistema = models.CharField(
        max_length=50,
        choices=[
            ('iucn', 'Lista Vermelha da IUCN'),
            ('brasil', 'Lista Nacional do ICMBio'),
            ('estadual', 'Lista Estadual'),
        ],
        default='iucn'
    )
    status = models.CharField(max_length=5, choices=STATUS_IUCNABR)
    ano_avaliacao = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.now().year)
        ]
    )
    
    class Meta:
        verbose_name = "Status de Conservação"
        verbose_name_plural = "Status de Conservação"
        ordering = ['-ano_avaliacao']
        
    def get_status_iucn(self):
        return self.statusconservacao_set.filter(sistema='IUCN').first()
    
    
class ImagemEspecieModel(models.Model):
    especie = models.ForeignKey(EspecieMarinhaModel, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='especies/')
    descricao = models.CharField(max_length=255, blank=True, null=True)
    credito = models.CharField(max_length=100, blank=True, null=True)


class NomeComumModel(models.Model):
    especie = models.ForeignKey(EspecieMarinhaModel, on_delete=models.CASCADE, related_name='nomes_comuns')
    nome = models.CharField(max_length=100)
    idioma = models.CharField(max_length=50, default='pt')
    regiao = models.CharField(max_length=100, blank=True, null=True)




class TipoAmeacaModel(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)  # 👈 ESTE CAMPO

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

GRAVIDADE_CHOICES = [
    ('alta', 'Alta'),
    ('media', 'Média'),
    ('baixa', 'Baixa'),
]
class AmeacaModel(models.Model):
    especie = models.ForeignKey(EspecieMarinhaModel, on_delete=models.CASCADE, related_name='ameacas')
    tipo = models.ForeignKey(TipoAmeacaModel, on_delete=models.PROTECT)
    descricao = models.TextField(blank=True, null=True)
    gravidade = models.CharField(max_length=50, choices=GRAVIDADE_CHOICES)
    slug = models.SlugField(unique=True, blank=True)
    
       
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)       
   


class UsoCulinarioModel(models.Model):
    TIPO_RECEITA_CHOICES = [
        ('entrada', 'Entrada'),
        ('principal', 'Prato Principal'),
        ('acompanhamento', 'Acompanhamento'),
        ('sobremesa', 'Sobremesa'),
        ('outro', 'Outro'),
    ]

    DIFICULDADE_CHOICES = [
        ('facil', 'Fácil'),
        ('medio', 'Médio'),
        ('dificil', 'Difícil'),
        ('chef', 'Nível Chef'),
    ]

    especie = models.ForeignKey(
        EspecieMarinhaModel,
        on_delete=models.CASCADE,
        related_name='receitas',
        verbose_name="Espécie Marinha"
    )
    nome_receita = models.CharField(max_length=200, verbose_name="Nome da Receita")
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_RECEITA_CHOICES,
        default='principal',
        verbose_name="Tipo de Receita"
    )
    dificuldade = models.CharField(
        max_length=50,
        choices=DIFICULDADE_CHOICES,
        default='medio',
        verbose_name="Nível de Dificuldade"
    )
    tempo_preparo = models.PositiveIntegerField(
        verbose_name="Tempo de Preparo (minutos)",
        help_text="Tempo total em minutos"
    )
    porcoes = models.PositiveIntegerField(
        verbose_name="Rendimento (porções)",
        validators=[MinValueValidator(1)]
    )
    ingredientes = models.TextField(verbose_name="Ingredientes")
    modo_preparo = models.TextField(verbose_name="Modo de Preparo")
    dicas = models.TextField(blank=True, null=True, verbose_name="Dicas e Variações")
    imagem = models.ImageField(
        upload_to='receitas/',
        blank=True,
        null=True,
        verbose_name="Foto da Receita Pronta"
    )
    fonte = models.CharField(max_length=200, blank=True, null=True, verbose_name="Fonte da Receita")
    link_referencia = models.URLField(blank=True, null=True, verbose_name="Link da Referência")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Uso Culinário"
        verbose_name_plural = "Usos Culinários"
        ordering = ['nome_receita']
        indexes = [
            models.Index(fields=['nome_receita']),
            models.Index(fields=['especie']),
        ]

    def __str__(self):
        return f"{self.nome_receita} ({self.especie.nome_comum})"

    def get_tempo_formatado(self):
        horas = self.tempo_preparo // 60
        minutos = self.tempo_preparo % 60
        if horas > 0:
            return f"{horas}h {minutos}min"
        return f"{minutos}min"

