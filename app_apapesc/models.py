from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone

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
EMISSOR_RG_CHOICES = [
    ('SSP/AC', 'SSP/AC'),
    ('SSP/AL', 'SSP/AL'),
    ('SSP/AP', 'SSP/AP'),
    ('SSP/AM', 'SSP/AM'),
    ('SSP/BA', 'SSP/BA'),
    ('SSP/CE', 'SSP/CE'),
    ('SSP/DF', 'SSP/DF'),
    ('SSP/ES', 'SSP/ES'),
    ('SSP/GO', 'SSP/GO'),
    ('SSP/MA', 'SSP/MA'),
    ('SSP/MG', 'SSP/MG'),
    ('SSP/MS', 'SSP/MS'),
    ('SSP/MT', 'SSP/MT'),
    ('SSP/PA', 'SSP/PA'),
    ('SSP/PB', 'SSP/PB'),
    ('SSP/PE', 'SSP/PE'),
    ('SSP/PI', 'SSP/PI'),
    ('SSP/RJ', 'SSP/RJ'),
    ('SSP/RN', 'SSP/RN'),
    ('SSP/RS', 'SSP/RS'),
    ('SSP/RO', 'SSP/RO'),
    ('SSP/RR', 'SSP/RR'),
    ('SSP/SC', 'SSP/SC'),
    ('SSP/SP', 'SSP/SP'),
    ('SSP/SE', 'SSP/SE'),
    ('SSP/TO', 'SSP/TO'),
    ('UF', 'UF'),
    ('Não declarado', 'Não declarado'),
]

# INTEGRANTES
class IntegrantesModel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="integrante"
    )
    cpf = models.CharField(
        max_length=14,
        unique=True,
        verbose_name="CPF"
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
    email = models.EmailField(
        blank=True, null=True, 
        verbose_name="E-mail"
    )
    foto = models.ImageField(
        upload_to='fotos_associados/', 
        blank=True, null=True
    )
    data_nascimento = models.DateField(
        blank=True, null=True, 
        verbose_name="Data de Nascimento"
    )
    naturalidade = models.CharField(
        max_length=100, 
        blank=True, null=True
    )
    # Documento RG
    rg_numero = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Número do RG", 
        blank=True, null=True
    )
    rg_orgao = models.CharField(
        max_length=50,
        choices=EMISSOR_RG_CHOICES,
        default='Não declarado', 
        verbose_name="RG-Orgão Emissor"
    )
    rg_data_emissao = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Emissão do RG"
    )
    reparticao = models.ForeignKey(
        'ReparticoesModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="integrantes",
        verbose_name="Repartição",
        default=""
    )

    cargo = models.ForeignKey(
        'CargosModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cargo"
    )
    # Endereço residencial do integrante
    logradouro = models.CharField(
        max_length=255, 
        verbose_name="Logradouro", 
        help_text="Ex: Rua, Servidão, Travessa",
        default="", 
        blank=True, 
        null=True
    )
    bairro = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        default=""
    )
    numero = models.CharField(
        max_length=10, 
        default="", 
        blank=True, 
        null=True, 
        verbose_name="Número"
    )
    complemento = models.CharField(
        max_length=255, 
        blank=True, 
        null=True
    )
    cep = models.CharField(
        max_length=9,  # Apenas números (sem o hífen)
        validators=[RegexValidator(r'^\d{5}-\d{3}$', 'CEP deve estar no formato 00000-000.')],
        default="", 
        blank=True, 
        null=True,
        verbose_name="CEP"
    )
    municipio = models.CharField(
        max_length=100, 
        default="", 
        blank=True, 
        null=True
    )
    uf = models.CharField(
        max_length=50, 
        choices=UF_CHOICES, 
        default="Não declarado", 
        blank=True, 
        null=True, 
        verbose_name="Estado"
    )
    data_entrada = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Entrada"
    )
    data_saida = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Saida"
    )


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.cargo})"


# ========================================

# CARGOS
class CargosModel(models.Model):
    nome = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name="Nome do Cargo"
    )

    def __str__(self):
        return self.nome

# ========================================    

# MUNICIPIOS DE CIRCUNSCRIÇÂO
class MunicipiosModel(models.Model):
    municipio = models.CharField(
        max_length=120
    )
    uf = models.CharField(
        max_length=50, 
        choices=UF_CHOICES, 
        default="Não declarado", 
        blank=True, null=True, 
        verbose_name="Estado"
    )
    def __str__(self):
        return self.municipio

# ========================================

# APAPESC - Modelo Principal
class ApapescModel(models.Model):
    nome_fantasia = models.CharField(
        max_length=255, 
        verbose_name="Nome Fantasia"
    )
    razao_social = models.CharField(
        max_length=255, 
        verbose_name="Razão Social"
    )
    cnpj = models.CharField(
        max_length=18, 
        unique=True, 
        verbose_name="CNPJ"
    )
    # Dados de contato da Repartição
    celular = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                r'^\(\d{2}\)\d{5}-\d{4}$',  # Garante que o número seja no formato (XX)XXXXX-XXXX
                'Número inválido. O telefone deve conter 10 ou 11 dígitos, ex: (48)99999-9999.'
            )
        ]
    )  
    email = models.EmailField(
        unique=True, 
        blank=True, 
        null=True
    )
    telefone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True
    )

    # Relacionamentos para cargos principais
    administrador = models.OneToOneField(
        IntegrantesModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="administrador_apapesc",
        verbose_name="Administrador"
    )    
    presidente = models.OneToOneField(
        IntegrantesModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="presidente_apapesc",
        verbose_name="Presidente"
    )
    diretores = models.ManyToManyField(
        IntegrantesModel,
        blank=True,
        related_name="diretores_apapesc",
        verbose_name="Diretores"
    )
    # Lista de fundadores como texto livre
    fundadores = models.TextField(
        verbose_name="Fundadores", 
        help_text="Lista de fundadores da associação"
    )
    
    # Endereço Apapesc
    logradouro = models.CharField(
        max_length=255, 
        verbose_name="Logradouro", 
        help_text="Ex: Rua, Servidão, Travessa",
        default="", 
        blank=True, 
        null=True
    )
    bairro = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        default=""
    )
    numero = models.CharField(
        max_length=10, 
        default="", 
        blank=True, 
        null=True, 
        verbose_name="Número"
    )
    complemento = models.CharField(
        max_length=255, 
        blank=True, null=True
    )
    cep = models.CharField(
        max_length=9,  # Apenas números (sem o hífen)
        validators=[RegexValidator(r'^\d{5}-\d{3}$', 'CEP deve estar no formato 00000-000.')],
        default="", 
        blank=True, 
        null=True,
        verbose_name="CEP"
    )
    municipio = models.CharField(
        max_length=100, 
        default="", 
        blank=True, 
        null=True
    )
    uf = models.CharField(
        max_length=50, 
        choices=UF_CHOICES, 
        default="Não declarado", 
        blank=True, 
        null=True, 
        verbose_name="Estado"
    )
    # Datas
    data_abertura = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Abertura"
    )
    # Datas
    data_encerramento = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Encerramento"
    )   


    class Meta:
        verbose_name = "Apapesc"
        ordering = ['nome_fantasia']

    def __str__(self):
        return f"{self.nome_fantasia} ({self.razao_social})"


# ========================================

# REPARTIÇÔES
class ReparticoesModel(models.Model):
    apapesc = models.ForeignKey(
        ApapescModel,
        on_delete=models.CASCADE,
        related_name='reparticoes',
        verbose_name="Apapesc",
        default=1
    )
    nome_reparticao = models.CharField(
        max_length=120
    )
    municipio_sede = models.ForeignKey(
        MunicipiosModel,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='sedes'
    )     
    delegado = models.OneToOneField(
        IntegrantesModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delegado_apapesc",
        verbose_name="Delegado"
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
    email = models.EmailField(
        blank=True, 
        null=True, 
        verbose_name="E-mail"
    )
    # Endereço da Repartição
    logradouro = models.CharField(
        max_length=255, 
        verbose_name="Logradouro", 
        help_text="Ex: Rua, Servidão, Travessa",
        default="", 
        blank=True, 
        null=True
    )
    bairro = models.CharField(
        max_length=100, 
        blank=True, null=True, 
        default=""
    )
    numero = models.CharField(
        max_length=10, 
        default="", 
        blank=True, 
        null=True, 
        verbose_name="Número"
    )
    complemento = models.CharField(
        max_length=255, 
        blank=True, null=True
    )
    cep = models.CharField(
        max_length=9,  # Apenas números (sem o hífen)
        validators=[RegexValidator(r'^\d{5}-\d{3}$', 'CEP deve estar no formato 00000-000.')],
        default="", 
        blank=True, 
        null=True,
        verbose_name="CEP"
    )
    municipio = models.CharField(
        max_length=100, 
        default="", 
        blank=True, 
        null=True
    )
    uf = models.CharField(
        max_length=50, 
        choices=UF_CHOICES, 
        default="Não declarado", 
        blank=True, null=True, 
        verbose_name="Estado"
    )
    # Municípios de Circunscrição
    municipios_circunscricao = models.ManyToManyField(
        MunicipiosModel,
        max_length=100, 
        default="", 
        blank=True
    )
    # Datas
    data_abertura = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Abertura"
    )
    # Datas
    data_encerramento = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Encerramento"
    )        

    
    def __str__(self):
        return self.nome_reparticao
    
# ========================================
