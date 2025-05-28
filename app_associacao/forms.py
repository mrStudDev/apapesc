from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from django.contrib.auth.models import Group

from .models import(
    AssociacaoModel,
    IntegrantesModel,
    ReparticoesModel,
    MunicipiosModel,
    CargosModel,
    
)
from app_associados.models import ProfissoesModel

class AssociacaoForm(forms.ModelForm):
    diretores = forms.ModelMultipleChoiceField(
        queryset=IntegrantesModel.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'size': '15',
            }
        ),
        label="Diretores"
    )
            
    class Meta:

        model = AssociacaoModel
        fields = '__all__'
        widgets = {
            'nome_fantasia': forms.TextInput(attrs={
                'placeholder': 'Digite o Nome Fantasia',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),

            'razao_social': forms.TextInput(attrs={
                'placeholder': 'Nome Fantasia',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemplo@email.com',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-blue-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),            
            'cnpj': forms.TextInput(attrs={
                'placeholder': '00.000.000/0000-00 Numero do CNPJ',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'celular': forms.TextInput(attrs={
                'placeholder': '(99)99999-9999',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraTelefone(this)',  # Chama a função de máscara para celular
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': 'telefone (00) 0000-0000',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),            
            'data_abertura': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),
            'data_encerramento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),                                                          
            'fundadores': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'administrador': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'presidente': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
           
            # Endereço Associação
            'logradouro': forms.TextInput(attrs={
                'placeholder': 'Rua / Servidão / Avenida',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'bairro': forms.TextInput(attrs={
                'placeholder': 'Bévili-Rios / Vila Joana / Jardim das Flores',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'numero': forms.TextInput(attrs={
                'placeholder': '0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'complemento': forms.TextInput(attrs={
                'placeholder': 'Casa / Apto 71 / Quarto 10',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'cep': forms.TextInput(attrs={
                'placeholder': '00000-000',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraCEP(this)'
            }),
            'municipio': forms.TextInput(attrs={
                'placeholder': 'Nome da cidade',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'uf': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),                                         
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['diretores'].initial = self.instance.diretores.all()

    def clean_diretores(self):
        diretores = self.cleaned_data.get('diretores')
        # Se quiser obrigar a ter pelo menos 1, tudo bem.
        if not diretores:
            raise forms.ValidationError("Selecione ao menos um diretor.")
        return diretores

    def clean_data_abertura(self):
        data = self.cleaned_data.get('data_abertura')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_data_encerramento(self):
        data = self.cleaned_data.get('data_encerramento')
        if not data:
            return None  # Permita valores nulos
        return data
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if not cep:
            return cep  
        
        numeros = ''.join(c for c in cep if c.isdigit())
        
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")
        
        return f"{numeros[:5]}-{numeros[5:]}"
    
    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        # Remove caracteres não numéricos da string, como parênteses, hífens e espaços
        numeros = ''.join(c for c in celular if c.isdigit())
        # Verifique se o número tem 10 ou 11 dígitos
        if len(numeros) < 10 or len(numeros) > 11:
            raise ValidationError("O celular deve conter 10 ou 11 dígitos.")
        # Se você desejar, pode formatar o celular de volta ao formato desejado:
        celular_formatado = f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"
        return celular_formatado



class ReparticaoForm(forms.ModelForm):
    municipios_circunscricao = forms.ModelMultipleChoiceField(
        queryset=ReparticoesModel.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'size': '15',
            }
        ),
        label="municipios_circunscricao"
    )    
    class Meta:
        model = ReparticoesModel
        fields = '__all__'
        widgets = {
            'associacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),            
            'nome_reparticao': forms.TextInput(attrs={
                'placeholder': 'Repartição de "Nome do Município',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemplo@email.com',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-blue-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),               
            'celular': forms.TextInput(attrs={
                'placeholder': '(99)99999-9999',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraTelefone(this)',  # Chama a função de máscara para celular
            }),  
            'municipio_sede': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),  
            'delegado': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),               
            # Endereço Repartição
            'logradouro': forms.TextInput(attrs={
                'placeholder': 'Rua / Servidão / Avenida',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'bairro': forms.TextInput(attrs={
                'placeholder': 'Bévili-Rios / Vila Joana / Jardim das Flores',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'numero': forms.TextInput(attrs={
                'placeholder': '0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'complemento': forms.TextInput(attrs={
                'placeholder': 'Casa / Apto 71 / Quarto 10',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'cep': forms.TextInput(attrs={
                'placeholder': '00000-000',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraCEP(this)'
            }),
            'municipio': forms.TextInput(attrs={
                'placeholder': 'Nome da cidade',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'uf': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),               
            'data_abertura': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),
            'data_encerramento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),                               
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['municipios_circunscricao'].initial = self.instance.municipios_circunscricao.all()

 # 👉 Inicializa seleção de municípios atuais (quando for edição)
        if self.instance and self.instance.pk:
            self.fields['municipios_circunscricao'].initial = self.instance.municipios_circunscricao.all()

        # ⚙️ Lista de todos os municípios já vinculados a alguma repartição
        municipios_ja_vinculados = MunicipiosModel.objects.filter(
            municipios_circunscricao__isnull=False
        ).distinct()

        # 🔥 Remove os da própria repartição (se for edição)
        if self.instance and self.instance.pk:
            municipios_na_propria = self.instance.municipios_circunscricao.all()
            municipios_ocupados = municipios_ja_vinculados.exclude(id__in=municipios_na_propria)
        else:
            municipios_ocupados = municipios_ja_vinculados

        # 🏷️ Salva ocupados para template
        self.municipios_ocupados = municipios_ocupados

        # 🚀 Queryset dos livres: todos - ocupados
        municipios_livres = MunicipiosModel.objects.exclude(id__in=municipios_ocupados)

        # ✅ Atribui apenas aqui corretamente
        self.fields['municipios_circunscricao'].queryset = municipios_livres | (self.instance.municipios_circunscricao.all() if self.instance and self.instance.pk else MunicipiosModel.objects.none())

        # 👉 Outros campos seguem configurados normalmente
        self.fields['associacao'].queryset = AssociacaoModel.objects.all()
        self.fields['associacao'].label_from_instance = lambda obj: obj.nome_fantasia

        self.fields['municipio_sede'].queryset = MunicipiosModel.objects.all()
        self.fields['delegado'].queryset = IntegrantesModel.objects.all()

    def clean_municipios_circunscricao(self):
        municipios_circunscricao = self.cleaned_data.get('municipios_circunscricao')
        # Se quiser obrigar a ter pelo menos 1, tudo bem.
        if not municipios_circunscricao:
            raise forms.ValidationError("Selecione ao menos um Município.")
        return municipios_circunscricao
    
                
    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        # Remove caracteres não numéricos da string, como parênteses, hífens e espaços
        numeros = ''.join(c for c in celular if c.isdigit())
        # Verifique se o número tem 10 ou 11 dígitos
        if len(numeros) < 10 or len(numeros) > 11:
            raise ValidationError("O celular deve conter 10 ou 11 dígitos.")
        # Se você desejar, pode formatar o celular de volta ao formato desejado:
        celular_formatado = f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"
        return celular_formatado
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if not cep:
            return cep  
        
        numeros = ''.join(c for c in cep if c.isdigit())
        
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")
        
        return f"{numeros[:5]}-{numeros[5:]}"
    
    def clean_data_abertura(self):
        data = self.cleaned_data.get('data_abertura')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_data_encerramento(self):
        data = self.cleaned_data.get('data_encerramento')
        if not data:
            return None  # Permita valores nulos
        return data

class IntegranteForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all().order_by('name'),
        required=True,
        label="Grupo",
        help_text="Selecione o grupo ao qual o integrante será adicionado.",
        widget=forms.Select(
            attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }
        )
    )
    
    class Meta:
        model = IntegrantesModel
        fields = '__all__'
        widgets = {
            'associacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'reparticao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),   
            'cargo': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),                                             
            # Informações Pessoais
            'cpf': forms.TextInput(attrs={
                'id': 'id_cpf',
                'placeholder': '000.000.000-00',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraCPF(this)',  # Chama a função de máscara para CPF
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemplo@email.com',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-blue-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),               
            'celular': forms.TextInput(attrs={
                'placeholder': '(99)99999-9999',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraTelefone(this)',  # Chama a função de máscara para celular
            }), 
            'oab': forms.TextInput(attrs={
                'placeholder': 'Digite somente números 0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'nacionalidade': forms.TextInput(attrs={
                'placeholder': 'País de Origem - brasileiro(a)',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),            
            # Documento RG
            'rg_numero': forms.TextInput(attrs={
                'placeholder': 'Digite somente números 0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'rg_orgao': forms.Select(attrs={
                'placeholder': 'SSP/UF',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'rg_data_emissao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),
            'naturalidade': forms.TextInput(attrs={
                'placeholder': 'Local de nascimento',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),                      
            # Informações Pessoais
            'foto': forms.FileInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'estado_civil': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'profissao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
                    
            # Endereço Repartição
            'logradouro': forms.TextInput(attrs={
                'placeholder': 'Rua / Servidão / Avenida',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'bairro': forms.TextInput(attrs={
                'placeholder': 'Bévili-Rios / Vila Joana / Jardim das Flores',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'numero': forms.TextInput(attrs={
                'placeholder': '0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'complemento': forms.TextInput(attrs={
                'placeholder': 'Casa / Apto 71 / Quarto 10',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'cep': forms.TextInput(attrs={
                'placeholder': '00000-000',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraCEP(this)'
            }),
            'municipio': forms.TextInput(attrs={
                'placeholder': 'Nome da cidade',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'uf': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),     
            'data_entrada': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),
            'data_saida': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),                           
        }
        
    def __init__(self, *args, **kwargs):
        # Recupera o usuário do kwargs
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['user'].initial = user
        
        # Configura o valor inicial para o campo 'group'
        if self.instance.pk and self.instance.user.groups.exists():
            self.fields['group'].initial = self.instance.user.groups.first()
            
        # Configura o queryset do campo 'group' para excluir determinados grupos
        excluded_groups = ['Associados da Associação', 'User Vip']  # Grupos a serem excluídos
        self.fields['group'].queryset = Group.objects.exclude(name__in=excluded_groups).order_by('name')

        # Configura os querysets dos outros campos relacionados
        #self.fields['associacao'].queryset = AssociacaoModel.objects.all()
        self.fields['cargo'].queryset = CargosModel.objects.all()
       # self.fields['reparticao'].queryset = ReparticoesModel.objects.all()
        self.fields['profissao'].queryset = ProfissoesModel.objects.all().order_by('nome')

        # Configurações de Associação
        self.fields['associacao'].queryset = AssociacaoModel.objects.all()
        self.fields['associacao'].label_from_instance = lambda obj: obj.nome_fantasia

        # Configurações de Repartições
        self.fields['reparticao'].queryset = ReparticoesModel.objects.all()
        self.fields['reparticao'].label_from_instance = lambda obj: obj.nome_reparticao


                        
    # Validação dos dígitos verificadores do CPF
    def calcular_digito(cpf_parcial):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(len(cpf_parcial) + 1, 1, -1)))
        resto = (soma * 10) % 11
        return resto if resto < 10 else 0

        if calcular_digito(numeros[:9]) != int(numeros[9]) or calcular_digito(numeros[:10]) != int(numeros[10]):
            raise ValidationError("CPF inválido.")

        return numeros
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf:
            return cpf  # Retorna sem validação adicional se CPF estiver vazio

        # Verifica se o CPF já existe em outra instância
        queryset = IntegrantesModel.objects.filter(cpf=cpf)
        if self.instance and self.instance.pk:
            # Exclui o próprio objeto da verificação
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError("Este CPF já está cadastrado em outro associado.")
        return cpf
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if not cep:
            return cep  
        
        numeros = ''.join(c for c in cep if c.isdigit())
        
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")
        
        return f"{numeros[:5]}-{numeros[5:]}"

    def clean_data_nascimento(self):
        data = self.cleaned_data.get('data_nascimento')
        if not data:
            return self.initial.get('data_nascimento') or self.instance.data_nascimento
        return data


    def clean_data_emissao(self):
        data = self.cleaned_data.get('data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data 
    
    def clean_data_entrada(self):
        data = self.cleaned_data.get('data_entrada')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_data_saida(self):
        data = self.cleaned_data.get('data_saida')
        if not data:
            return None  # Permita valores nulos
        return data
    
class MunicipioForm(forms.ModelForm):
    class Meta:
        model = MunicipiosModel
        fields = '__all__'
        widgets = {
            'municipio': forms.TextInput(attrs={
                'placeholder': 'Digite o nome do Município',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
            }),
            'uf': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),                        
        }


    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        # Remove caracteres não numéricos da string, como parênteses, hífens e espaços
        numeros = ''.join(c for c in celular if c.isdigit())
        # Verifique se o número tem 10 ou 11 dígitos
        if len(numeros) < 10 or len(numeros) > 11:
            raise ValidationError("O celular deve conter 10 ou 11 dígitos.")
        # Se você desejar, pode formatar o celular de volta ao formato desejado:
        celular_formatado = f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"

        return celular_formatado

    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        # Se o CEP não for preenchido, retorna None ou string vazia
        if not cep:
            return cep  # Retorna o valor original sem validar
        # Remove o hífen e valida se o valor tem apenas dígitos
        numeros = ''.join(c for c in cep if c.isdigit())
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")

        return numeros  # Retorna apenas os números do celular

