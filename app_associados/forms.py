from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from .models import AssociadoModel, ProfissoesModel
import bleach
from app_associacao.models import AssociacaoModel, ReparticoesModel, MunicipiosModel


class AssociadoForm(forms.ModelForm):
    class Meta:
        model = AssociadoModel
        fields = '__all__'
        widgets = {
            # Informações Vinculo
            'associacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'reparticao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'municipio_circunscricao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'data_filiacao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 bg-gray-50 text-gray-500 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }, format='%Y-%m-%d'),

            'status': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-500 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'data_desfiliacao': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-500 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'id': 'id_data_desfiliacao',
                },
                format='%Y-%m-%d'
            ),
            
            #Informações de Contato - Documentos e informações de Principais
            'celular': forms.TextInput(attrs={
                'placeholder': '(99)99999-9999',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 bg-gray-50 text-gray-500 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraTelefone(this)',  # Chama a função de máscara para celular
            }),
            'celular_correspondencia': forms.TextInput(attrs={
                'placeholder': '(99)99999-9999',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 bg-gray-50 text-gray-500 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraTelefone(this)',  # Chama a função de máscara para celular
            }),
            'drive_folder_id': forms.TextInput(attrs={
                'class': 'bg-gray-100 border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight shadow-sm',
                'readonly': 'readonly',  # Torna o campo ineditável
                'style': 'cursor: not-allowed;'  # Estilo para indicar que não pode ser editado
            }),
            'cpf': forms.TextInput(attrs={
                'id': 'id_cpf',
                'placeholder': '000.000.000-00',
                'class': 'appearance-none border border-yellow-300 rounded-md w-full py-2 px-3 bg-gray-50 text-gray-500 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraCPF(this)',  # Chama a função de máscara para CPF
            }),
            'senha_gov': forms.TextInput(attrs={
                'class': 'appearance-none border border-yellow-300 rounded-md w-full py-2 px-3 bg-gray-50 text-gray-500 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemplo@email.com',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 bg-gray-50 text-gray-500 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'senha_google': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 bg-gray-50 text-gray-400 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'senha_site': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 bg-gray-50 text-gray-500 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),                   
            # Documento RG
            'rg_numero': forms.TextInput(attrs={
                'placeholder': 'Digite somente números 0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-blue-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
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
            # Documentação de Habilitação CNH
            'cnh': forms.TextInput(attrs={
                'placeholder': '00000000',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'cnh_uf': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),            
            'cnh_data_emissao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),
            'cnh_data_validade': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),                        
            # Informações Pessoais
            'foto': forms.FileInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'apelido': forms.TextInput(attrs={
                'placeholder': 'Carinhosamente Chamado como... (somente apelidos carinhosos)',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),            
            'sexo_biologico': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'etnia': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'escolaridade': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'nome_mae': forms.TextInput(attrs={
                'placeholder': 'Nome da Mãe',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'nome_pai': forms.TextInput(attrs={
                'placeholder': 'Nome da Pai',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'estado_civil': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'profissao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            
            # Informações de Singulares de Atividade do Associado
            'recolhe_inss': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'recebe_seguro': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),  
            'ja_recebeu_defeso_algumavez': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),                       
            'relacao_trabalho': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'comercializa_produtos': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'outra_fonte_renda': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }), 
            'casa_onde_mora': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),                        
            'bolsa_familia': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            # Identificacoes Oficiais/Números Cidadão INSS/NIT/PIS/TITULO
            'nit': forms.TextInput(attrs={
                'placeholder': '0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'pis': forms.TextInput(attrs={
                'placeholder': '0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'caepef': forms.TextInput(attrs={
                'placeholder': '0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'cei': forms.TextInput(attrs={
                'placeholder': '0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'titulo_eleitor': forms.TextInput(attrs={
                'placeholder': '0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            
            # Documentação Profissional
            'rgp': forms.TextInput(attrs={
                'placeholder': 'SCH00000000',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'rgp_data_emissao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),
            'primeiro_registro': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),
            'rgp_mpa': forms.TextInput(attrs={
                'placeholder': 'EX: MPA',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),

            # Documentação de Trabalho
            'ctps': forms.TextInput(attrs={
                'placeholder': '0123456789',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'ctps_serie': forms.TextInput(attrs={
                'placeholder': '',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'ctps_data_emissao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),
            'ctps_uf': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),

            # Dados de Produção Média Anual
            'especie1': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'quantidade1': forms.TextInput(attrs={
                'placeholder': '000.000,00',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'preco1': forms.TextInput(attrs={
                'placeholder': 'Preço por Kg (R$)',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            
            'especie2': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'quantidade2': forms.TextInput(attrs={
                'placeholder': '000.000,00',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'preco2': forms.TextInput(attrs={
                'placeholder': 'Preço por Kg (R$)',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            
            'especie3': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'quantidade3': forms.TextInput(attrs={
                'placeholder': '000.000,00',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'preco3': forms.TextInput(attrs={
                'placeholder': 'Preço por Kg (R$)',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            
            'especie4': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'quantidade4': forms.TextInput(attrs={
                'placeholder': '000.000,00',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'preco4': forms.TextInput(attrs={
                'placeholder': 'Preço por Kg (R$)',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            
            'especie5': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'quantidade5': forms.TextInput(attrs={
                'placeholder': '000.000,00',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'preco5': forms.TextInput(attrs={
                'placeholder': 'Preço por Kg (R$)',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            
            # Endereço residencial
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
                'oninput': 'mascaraCEP(this)'  # Chama a função de máscara para CEP
            }),
            'municipio': forms.TextInput(attrs={
                'placeholder': 'Nome da cidade',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'uf': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            # Atualização de Dados
            'data_atualizacao': forms.DateInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }, format='%Y-%m-%d'),            

        }

        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        associacao = kwargs.pop('associacao', None)
        reparticao = kwargs.pop('reparticao', None)
        super().__init__(*args, **kwargs)
    
        # Filtra repartições com base na associação
        if associacao:
            self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao=associacao)
        else:
            self.fields['reparticao'].queryset = ReparticoesModel.objects.none()

        # Filtra municípios com base na repartição
        if reparticao:
            self.fields['municipio_circunscricao'].queryset = MunicipiosModel.objects.filter(reparticao=reparticao)
        else:
            self.fields['municipio_circunscricao'].queryset = MunicipiosModel.objects.none()
            
        # Se o formulário tiver uma instância associada a um usuário, define o e-mail inicial
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
        elif user:
            # Caso um novo associado, tenta usar o usuário passado explicitamente
            self.fields['email'].initial = user.email
        # Tornar o campo e-mail somente leitura
        self.fields['email'].widget.attrs['readonly'] = True
        
        # Personalize os campos de espécie e quantidade, se necessário
        for i in range(1, 5):
            self.fields[f'especie{i}'].widget.attrs.update({
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
            self.fields[f'quantidade{i}'].widget.attrs.update({
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Digite a quantidade em Kg',
                'step': '0.01'
            })
        
        # Configuração de campos adicionais
        self.fields['profissao'].queryset = ProfissoesModel.objects.all().order_by('nome')
        self.fields['content'].widget = forms.Textarea(attrs={'class': 'hidden-editor'})
        self.fields['estado_civil'].choices = sorted(
            self.fields['estado_civil'].choices,
            key=lambda choice: choice[1]
        )
        # Configurações de Associação
        self.fields['associacao'].queryset = AssociacaoModel.objects.all()
        self.fields['associacao'].label_from_instance = lambda obj: obj.nome_fantasia

        # Configurações de Repartições
        self.fields['reparticao'].queryset = ReparticoesModel.objects.all()
        self.fields['reparticao'].label_from_instance = lambda obj: obj.nome_reparticao

        # Configurações de Municípios
        self.fields['municipio_circunscricao'].queryset = MunicipiosModel.objects.all()
        self.fields['municipio_circunscricao'].label_from_instance = lambda obj: obj.municipio
        
        # Campos nome_pai e nome_mae devem sempre vir da instância
        self.fields['nome_mae'].initial = self.instance.nome_mae
        self.fields['nome_pai'].initial = self.instance.nome_pai

    def clean(self):
        cleaned_data = super().clean()

        for i in range(1, 6):
            key = f'preco{i}'
            valor = cleaned_data.get(key)

            if isinstance(valor, str) and valor.strip() != "":
                try:
                    # Converte '19,88' → Decimal('19.88')
                    cleaned_data[key] = Decimal(valor.replace('.', '').replace(',', '.'))
                except InvalidOperation:
                    self.add_error(key, "Preço inválido. Use o formato 00,00.")
            elif valor == "":
                cleaned_data[key] = None  # Se quiser limpar caso o campo esteja vazio

        return cleaned_data

    def clean_user(self):
        # Não permitir alteração do campo `user` na edição
        if self.instance.pk:
            return self.instance.user
        return self.cleaned_data.get('user')
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf:
            return cpf  # Retorna sem validação adicional se CPF estiver vazio

        # Verifica se o CPF já existe em outra instância
        queryset = AssociadoModel.objects.filter(cpf=cpf)
        if self.instance and self.instance.pk:
            # Exclui o próprio objeto da verificação
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError("Este CPF já está cadastrado em outro associado.")
        return cpf
                
    # Validação dos dígitos verificadores do CPF
    def calcular_digito(cpf_parcial):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(len(cpf_parcial) + 1, 1, -1)))
        resto = (soma * 10) % 11
        return resto if resto < 10 else 0

        if calcular_digito(numeros[:9]) != int(numeros[9]) or calcular_digito(numeros[:10]) != int(numeros[10]):
            raise ValidationError("CPF inválido.")

        return numeros

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

    def clean_celular_correspondencia(self):
        celular_correspondencia = self.cleaned_data.get('celular_correspondencia')
        # Remove caracteres não numéricos da string, como parênteses, hífens e espaços
        numeros = ''.join(c for c in celular_correspondencia if c.isdigit())
        # Verifique se o número tem 10 ou 11 dígitos
        if len(numeros) < 10 or len(numeros) > 11:
            raise ValidationError("O celular deve conter 10 ou 11 dígitos.")
        # Se você desejar, pode formatar o celular de volta ao formato desejado:
        celular_correspondencia_formatado = f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"
        return celular_correspondencia_formatado    

    def clean_data_nascimento(self):
        data = self.cleaned_data.get('data_nascimento')
        if not data:
            return None  # Permita valores nulos
        return data
    def clean_data_filiacao(self):
        data = self.cleaned_data.get('data_filiacao')
        if not data:
            return None  # Permita valores nulos
        return data
    def clean_rg_data_emissao(self):
        data = self.cleaned_data.get('rg_data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data 
    
    def clean_rgp_data_emissao(self):
        data = self.cleaned_data.get('rgp_data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data
    
    def clean_primeiro_registro(self):
        data = self.cleaned_data.get('primeiro_registro')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_ctps_data_emissao(self):
        data = self.cleaned_data.get('ctps_data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data 
    
    def clean_cnh_data_emissao(self):
        data = self.cleaned_data.get('cnh_data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data 
        
    def clean_data_emissao(self):
            
        data = self.cleaned_data.get('data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        # Se o CEP não for preenchido, retorna None ou string vazia
        if not cep:
            return cep  # Retorna o valor original sem validar
        
        # Remove caracteres não numéricos
        numeros = ''.join(c for c in cep if c.isdigit())
        
        # Verifica se o CEP tem exatamente 8 dígitos
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")
        
        # Retorna o CEP formatado com o hífen
        return f"{numeros[:5]}-{numeros[5:]}"

    def clean_precos(self):
        cleaned_data = super().clean()
        for i in range(1, 6):
            key = f'preco{i}'
            valor = cleaned_data.get(key)
            if isinstance(valor, str):
                cleaned_data[key] = Decimal(valor.replace('.', '').replace(',', '.'))
        return cleaned_data

class ProfissaoForm(forms.ModelForm):
    class Meta:
        model = ProfissoesModel
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Digite o nome da profissão',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm'
            }),
        }