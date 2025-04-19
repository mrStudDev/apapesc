# app_embarcacoes/forms.py

from django import forms
from .models import EmbarcacoesModel
from app_associados.models import AssociadoModel

class EmbarcacaoForm(forms.ModelForm):
    class Meta:
        model = EmbarcacoesModel
        exclude = ['data_atualizacao']  # Atualizado automaticamente
        fields = '__all__'
        widgets = {
            'proprietario': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'destaque_embarcacao_img': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-700 border border-gray-300 rounded-md p-2 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            }),
            'inscricao_embarcacao': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Nº de inscrição da embarcação'
            }),
            'tipo_embarcacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
            }),
            'validade_tie': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
                },
                format='%Y-%m-%d'  # 💡 isso garante que o valor apareça no input type="date"
            ),
            'nome_embarcacao': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Nome da embarcação'
            }),
            'atividade': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Atividade da embarcação'
            }),
            'area_navegacao': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Área de navegação'
            }),
            'numero_tripulantes': forms.NumberInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Nº de tripulantes'
            }),
            'numero_passageiros': forms.NumberInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Nº de passageiros'
            }),
            'cumprimento': forms.NumberInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Comprimento (em metros)'
            }),
            'ab_gt': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'AB / GT'
            }),
            'boca': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Boca'
            }),
            'tipo_propulsao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
            }),
            'porte': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
            }),            
            'combustivel': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
            }),
            'motor_1': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Motor 1'
            }),
            'numero_serie_1': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Nº de série do motor 1'
            }),
            'potencia_hp1': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Potência HP'
            }),            
            'motor_2': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Motor 2'
            }),
            'numero_serie_2': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Nº de série do motor 2'
            }),
            'potencia_hp2': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Potência HP'
            }),             
            'motor_3': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Motor 3'
            }),
            'numero_serie_3': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Nº de série do motor 3'
            }),
            'potencia_hp3': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Potência HP'
            }),             
            'motor_4': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Motor 4'
            }),
            'numero_serie_4': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Nº de série do motor 4'
            }),
            'potencia_hp4': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Potência HP'
            }),
            'ano_construcao': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
                },
                format='%Y-%m-%d'  # 💡 isso garante que o valor apareça no input type="date"
            ),            
            'construtor_nome': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Construtor'
            }), 
            'material_construcao': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Material Construção / Madeira /'
            }), 
            'arqueacao_bruta': forms.NumberInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Medida (em metros)'
            }),                                               
            'traves_img': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-700 border border-gray-300 rounded-md p-2 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            }),            
            'popa_img': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-700 border border-gray-300 rounded-md p-2 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            }),            
            'co_proprietario_nome': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Nome do co-proprietário (opcional)'
            }),            
            'alienacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
            }),
            'municipio_emissao': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Município de emissão'
            }),
            'data_emissao': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
                },
                format='%Y-%m-%d'
            ),
            'seguro_dpen': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
            }), 
            'seguro_dpem_numero': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Processo SUSEP 1232456789 /'
            }),                        
            'seguro_dpem_data_vencimento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
                },
                format='%Y-%m-%d'
            ),            
            'content': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'rows': 4,
                'placeholder': 'Anotações ou observações'
            }),
        }
        
    def __init__(self, *args, proprietario=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Só exibe campo proprietário se for para edição (modo superuser ou admin, por exemplo)
        if proprietario:
            self.fields['proprietario'].initial = proprietario
            self.fields['proprietario'].widget = forms.HiddenInput()