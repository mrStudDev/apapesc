from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from bleach.sanitizer import Cleaner
from bleach.css_sanitizer import CSSSanitizer
from django.contrib.auth.models import Group
from .utils import create_associado_folder
from django.apps import apps
from django.db import transaction
from decimal import Decimal

from app_associacao.models import(
    AssociacaoModel,
    ReparticoesModel,
    MunicipiosModel,
)
# Choices para reutilização
SEXO_CHOICES = [
    ('Masculino', 'Masculino'),
    ('Feminino', 'Feminino'),
    ('Não declarado', 'Não declarado'),
]

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
STATUS_CHOICES = [
    ('Associado Lista Ativo(a)', 'Associado Lista Ativo(a)'),
    ('Associado Lista Aposentado(a)', 'Associado  Lista Aposentado(a)'),
    ('Candidato(a)', 'Candidato(a)'),
    ('Cliente Especial', 'Cliente Especial'),
    ('Desassociado(a)', 'Desassociado(a)'),
]
ESPECIES_MARITIMAS = [
    ('Abrótea', 'Abrótea'),
    ('Anchova', 'Anchova'),
    ('Atum', 'Atum'),
    ('Bagre', 'Bagre'),
    ('Baiacu', 'Baiacu'),
    ('Cação', 'Cação'),
    ('Cavala', 'Cavala'),
    ('Corvina', 'Corvina'),
    ('Garoupa', 'Garoupa'),
    ('Linguado', 'Linguado'),
    ('Marisco', 'Marisco'),
    ('Pampo', 'Pampo'),
    ('Pescada-olhuda', 'Pescada-olhuda'),
    ('Robalo', 'Robalo'),
    ('Sardinha', 'Sardinha'),
    ('Tainha', 'Tainha'),
    ('Xerelete', 'Xerelete'),
    ('Não declarado', 'Não declarado'),
]
ESTADO_CIVIL_CHOICES = [
    ('solteiro', 'solteiro'),
    ('solteira', 'solteira'),
    ('casado', 'casado'),
    ('casada', 'casada'),
    ('divorciado', 'divorciado'),
    ('divorciada', 'divorciada'),
    ('viúvo', 'viúvo'),
    ('viúva', 'viúva'),
    ('união estável', 'união estável'),  # Mantido original para consistência
    ('separado judicialmente', 'separado judicialmente'),
    ('separada judicialmente', 'separada judicialmente'),
    ('Não declarado', 'Não declarado'),

]
ETNIA_CHOICES = [
    ('Branco', 'Branco'),
    ('Pardo', 'Pardo'),
    ('Preto', 'Preto'),
    ('Amarelo', 'Amarelo'),
    ('Indígena', 'Indígena'),
    ('Outro', 'Outro'),
    ('Não declarado', 'Não declarado'),
]
ESCOLARIDADE_CHOICES = [
    ('Analfabeto', 'Analfabeto'),
    ('Primário 1/4 série', 'Primário 1/4 série'),
    ('Fundamental', 'Fundamental'),
    ('Ensino Médio', 'Ensino Médio'),
    ('Ensino Superior', 'Ensino Superior'),
    ('Não declarado', 'Não declarado'),
]
RECOLHE_INSS_CHOICES = [
    ('Sim', 'Sim'),
    ('Não', 'Não'),
    ('Não declarado', 'Não declarado'),
]
SEGURO_DEFESO_CHOICES = [
    ('Não Recebe', 'Não Recebe'),
    ('A partir de Dez', 'A partir de Dez'),
    ('A partir de Jan', 'A partir de Jan'),
    ('A partir de Fev', 'A partir de Fev'),
    ('A partir de Março', 'A partir de Março'),
    ('Não declarado', 'Não declarado'),     
]

class ProfissoesModel(models.Model):
    nome = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name="Profissão"
    )
    def __str__(self):
        return self.nome

# Create your models here.
class AssociadoModel(models.Model):
    # Usuarios associados - Acessos à perfís e notificações
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='associado',
        verbose_name="Usuário Associado"
    )    
    drive_folder_id = models.CharField(max_length=100, blank=True, null=True)
    # Informações Pessoais
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
    celular_correspondencia = models.CharField(
        max_length=15,
        default="",
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
    senha_google = models.CharField(
        max_length=128, 
        blank=True, 
        null=True,
        help_text="Senha criptografada para segurança.",
    )
    senha_site = models.CharField(
        max_length=128, 
        blank=True, 
        null=True,
        help_text="Senha criptografada para segurança.",
    )    
    foto = models.ImageField(
        upload_to='fotos_associados/', 
        blank=True, 
        null=True
    )
    sexo_biologico = models.CharField(
        max_length=15, 
        choices=SEXO_CHOICES,
        blank=True,
        default="Não declarado",
        verbose_name="Sexo Biológico"
    )
    etnia = models.CharField(
        max_length=15,
        blank=True,
        choices=ETNIA_CHOICES, 
        default="Não declarado",
        verbose_name="Etnia"
    )
    escolaridade = models.CharField(
        max_length=20,
        blank=True,
        choices=ESCOLARIDADE_CHOICES, 
        default="Não declarado",
        verbose_name="Escolaridade"
    )
    nome_mae = models.CharField(
        max_length=100, 
        verbose_name="Nome da Mãe", 
        blank=True, 
        null=True
    )
    nome_pai = models.CharField(
        max_length=100, 
        verbose_name="Nome do Pai", 
        blank=True, null=True
    )
    estado_civil = models.CharField(
        max_length=50, 
        choices=ESTADO_CIVIL_CHOICES, 
        blank=True, null=True, 
        verbose_name="Estado Civil",
        default="Não declarado"
    )
    profissao = models.ForeignKey(
        'ProfissoesModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Profissão"
    )
    recolhe_inss = models.CharField(
        max_length=50, 
        choices=RECOLHE_INSS_CHOICES, 
        blank=True, 
        null=True, 
        default="Não declarado"
    )
    recebe_seguro = models.CharField(
        max_length=50, 
        choices=SEGURO_DEFESO_CHOICES, 
        blank=True, 
        null=True, 
        default="Não declarado"
    )    
    # Documento RG
    rg_numero = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Número do RG", 
        blank=True, 
        null=True
    )
    rg_orgao = models.CharField(
        max_length=50,
        blank=True,
        choices=EMISSOR_RG_CHOICES,
        default='Não declarado',
        verbose_name="RG-Orgão Emissor"
    )
    rg_data_emissao = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data Emissão do RG"
    )
    naturalidade = models.CharField(
        max_length=100, 
        blank=True, 
        null=True
    )
    data_nascimento = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Nascimento"
    )
    # Documentos/Números Cidadão INSS/NIT/PIS/TITULO
    nit = models.CharField(
        max_length=25, 
        blank=True, 
        null=True, 
        verbose_name="Número do NIT", 
        unique=True
    )
    pis = models.CharField(
        max_length=25, 
        blank=True, 
        null=True, 
        verbose_name="Número do PIS"
    )
    titulo_eleitor = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Número do Título de Eleitor"
    )
    caepef = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Número do CAEPEF"
    )
    cei = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Número do CEI"
    )
   # Documentação Profissional
    rgp = models.CharField(
        max_length=25, 
        blank=True, 
        null=True, 
        verbose_name="Número do RGP", 
        unique=True
    )
    rgp_data_emissao = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data Emissão do RGP"
    )
    primeiro_registro = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data Primeiro Registro (RGP)"
    )
    rgp_mpa = models.CharField(
        blank=True, 
        null=True, 
        max_length=12, 
        verbose_name="Mapa do RGP"
    )

    # Documentação de Trabalho
    ctps = models.CharField(
        max_length=25, 
        blank=True, 
        null=True, 
        unique=True,
        verbose_name="Número Carteira Trabalho (CTPS)"
    )
    ctps_serie = models.CharField(
        max_length=25, 
        blank=True, 
        null=True, 
        verbose_name="CTPS - Série"
    )
    ctps_data_emissao = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data Emissão da CTPS"
    )
    ctps_uf = models.CharField(
        blank=True, 
        null=True, 
        max_length=50, 
        choices=UF_CHOICES, 
        default="Não declarado",
        verbose_name="CTPS UF"
    )
    # Documentação de Hanbilitação
    cnh = models.CharField(
        max_length=25, 
        blank=True, 
        null=True, 
        unique=True, 
        verbose_name="Núm. Registro da CNH"
    )
    cnh_data_emissao = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data Emissão da CNH"
    )

    # Endereço residencial
    logradouro = models.CharField(
        max_length=255, 
        verbose_name="Logradouro", 
        help_text="Ex: Rua, Servidão, Travessa",
        blank=True, 
        null=True
    )
    bairro = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
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
        validators=[RegexValidator(r'^\d{5}-\d{3}$', 'CEP deve estar no formato 00000-000')],
        default="", 
        blank=True, 
        null=True,
        verbose_name="CEP"
    )
    municipio = models.CharField(
        max_length=100, 
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
    # Vínculo
    associacao = models.ForeignKey(
        AssociacaoModel, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True, 
        related_name='associados_associacao',
        verbose_name="Associação"
    )
    reparticao = models.ForeignKey(
        ReparticoesModel, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True, 
        related_name='reparticoes_associados',
        verbose_name="Repartição"
    )
    municipio_circunscricao = models.ForeignKey(
        MunicipiosModel, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='municipios_associados',
        verbose_name="Município de Circunscrição/Atuação"
    )
    data_filiacao = models.DateField(
        null=True,
        verbose_name="Data da Filiação"
    )
    data_desfiliacao = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data da Desfiliação"
    )    
    status = models.CharField(
        max_length=40, 
        blank=True, 
        null=True, 
        choices=STATUS_CHOICES,
        verbose_name="Status",
        default="Candidato(a)"
    )
    # Espécies e Quantidades
    especie1 = models.CharField(
        max_length=50, 
        choices=ESPECIES_MARITIMAS, 
        blank=True, 
        null=True, 
        verbose_name="Espécie 1",
        default="Não declarado"
    )
    quantidade1 = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        verbose_name="Quantidade 1 (Kg)"
    )

    especie2 = models.CharField(
        max_length=50, 
        choices=ESPECIES_MARITIMAS, 
        blank=True, 
        null=True, 
        verbose_name="Espécie 2",
        default="Não declarado"
    )
    quantidade2 = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        verbose_name="Quantidade 2 (Kg)"
    )

    especie3 = models.CharField(
        max_length=50, 
        choices=ESPECIES_MARITIMAS, 
        blank=True, 
        null=True, 
        verbose_name="Espécie 3",
        default="Não declarado"
    )
    quantidade3 = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        verbose_name="Quantidade 3 (Kg)"
    )

    especie4 = models.CharField(
        max_length=50, choices=ESPECIES_MARITIMAS, 
        blank=True, 
        null=True, verbose_name="Espécie 4",
        default="Não declarado"
    )
    quantidade4 = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        verbose_name="Quantidade 4 (Kg)"
    )
    especie5 = models.CharField(
        max_length=50, 
        choices=ESPECIES_MARITIMAS, 
        blank=True, null=True, 
        verbose_name="Espécie 5",
        default="Não declarado"
    )
    quantidade5 = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        verbose_name="Quantidade 5 (Kg)"
    )
    data_atualizacao = models.DateField(
        auto_now=True
    )
    # Anotações
    content = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Anotações"
    )
    
    def save(self, *args, **kwargs):
        """
        Combina a lógica de sanitização do 'content',
        criação de pasta no Drive (se objeto for novo)
        e atribuição de anuidades ao associado.
        """
        # 1. Se houver campo 'content', sanitiza antes de salvar
        if hasattr(self, 'content') and self.content:
            allowed_tags = ['p', 'a', 'strong', 'em', 'ul', 'ol', 'li',
                            'blockquote', 'h1', 'h2', 'h3', 'br', 'span']
            allowed_attributes = {
                'a': ['href', 'title', 'style'],
                'span': ['style'],
                '*': ['style'],
            }
            allowed_styles = [
                'color', 'background-color', 'text-align',
                'font-weight', 'font-style', 'text-decoration'
            ]

            css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_styles)
            cleaner = Cleaner(
                tags=allowed_tags,
                attributes=allowed_attributes,
                strip=True,
                strip_comments=True,
                css_sanitizer=css_sanitizer
            )

            self.content = cleaner.clean(self.content)

        # 2. Se for a criação (não tem self.id ainda) e sem pasta Drive, cria pasta
        creating = not self.pk  # Detecta se é objeto novo
        if creating and not self.drive_folder_id:
            folder_name = self.user.get_full_name() or self.user.username
            parent_folder_id = '15Nby8u0aLy1hcjvfV8Ja6w_nSG0yFQ2w'  # Exemplo
            self.drive_folder_id = create_associado_folder(folder_name, parent_folder_id)

        # 3. Salva o objeto no banco
        super().save(*args, **kwargs)

        # 4. Depois de salvo (tem pk), atribui anuidades - Tentando ajustar o pipeline
        self.atribuir_anuidades_existentes()

    def atribuir_anuidades_existentes(self):
        AnuidadeModel = apps.get_model('app_finances', 'AnuidadeModel')
        AnuidadeAssociado = apps.get_model('app_finances', 'AnuidadeAssociado')
        
        anuidades = AnuidadeModel.objects.all()
        with transaction.atomic():
            for anuidade in anuidades:
                if not AnuidadeAssociado.objects.filter(anuidade=anuidade, associado=self).exists():
                    meses_restantes = self.calcular_meses_validos(anuidade.ano)
                    if meses_restantes > 0:
                        valor_pro_rata = round(
                            (anuidade.valor_anuidade / Decimal(12)) * Decimal(meses_restantes), 2
                        )
                        AnuidadeAssociado.objects.create(
                            anuidade=anuidade,
                            associado=self,
                            valor_pro_rata=valor_pro_rata
                        )

    def calcular_meses_validos(self, ano):
        """
        Calcula o número de meses para o cálculo pro-rata.
        """
        if not self.data_filiacao or self.data_filiacao.year > ano:
            return 0
        if self.data_filiacao.year == ano:
            # 12 - mês de filiação + 1 => filiou em março => 12 -3 + 1 = 10 meses
            return 12 - self.data_filiacao.month + 1
        return 12


    @property
    def drive_folder_link(self):
        if self.drive_folder_id:
            return f"https://drive.google.com/drive/folders/{self.drive_folder_id}"
        return None
    
    def __str__(self):
        return f"{self.user} - CPF: {self.cpf} - CELULAR: {self.celular} - {self.data_nascimento}"
