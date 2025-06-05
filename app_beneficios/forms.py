from django import forms
from .models import ControleBeneficioModel, BeneficioModel

from django import forms
from .models import ControleBeneficioModel

class ControleBeneficioForm(forms.ModelForm):
    class Meta:
        model = ControleBeneficioModel
        fields = [
            'status_pedido',
            'data_entrada',
            'numero_protocolo',
            'comprovante_protocolo',
            'anotacoes_exigencias',
            'anotacoes_gerais',
            'resultado_final',
        ]
        widgets = {
            'status_pedido': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 '
                         'leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'data_entrada': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 '
                         'leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }, format='%Y-%m-%d'),
            'numero_protocolo': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 '
                         'leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: 2025PROT000123'
            }),
            'comprovante_protocolo': forms.ClearableFileInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 '
                         'leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'anotacoes_exigencias': forms.Textarea(attrs={
                'rows': 3,
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 '
                         'leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Descreva as exigências recebidas, se houver'
            }),
            'anotacoes_gerais': forms.Textarea(attrs={
                'rows': 3,
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 '
                         'leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Notas e observações sobre o processo'
            }),
            'resultado_final': forms.Textarea(attrs={
                'rows': 3,
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 '
                         'leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: Deferido em 02/03/2025 conforme análise do INSS'
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garante que o formato da data seja interpretado corretamente
        self.fields['data_entrada'].input_formats = ['%Y-%m-%d']


class BeneficioModelForm(forms.ModelForm):
    class Meta:
        model = BeneficioModel
        fields = '__all__'
        widgets = {
            'nome': forms.Select(attrs={
                'class': 'form-select w-full text-sm border-gray-300 rounded-lg',
            }),
            'lei_federal': forms.TextInput(attrs={
                'class': 'form-input w-full text-sm border-gray-300 rounded-lg',
                'placeholder': 'Ex: Lei nº 10.779/2003',
            }),
            'instrucao_normativa': forms.TextInput(attrs={
                'class': 'form-input w-full text-sm border-gray-300 rounded-lg',
            }),
            'portaria': forms.TextInput(attrs={
                'class': 'form-input w-full text-sm border-gray-300 rounded-lg',
            }),
            'ano_concessao': forms.NumberInput(attrs={
                'class': 'form-input w-full text-sm border-gray-300 rounded-lg',
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select w-full text-sm border-gray-300 rounded-lg',
            }),
            'data_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input w-full text-sm border-gray-300 rounded-lg',
            }, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input w-full text-sm border-gray-300 rounded-lg',
            }, format='%Y-%m-%d'),
            'anotacoes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-textarea w-full text-sm border-gray-300 rounded-lg',
            }),
        }
    def __init__(self, *args, **kwargs):
        modo_edicao = kwargs.pop('modo_edicao', False)  # 👈 isso é o que estava faltando!
        super().__init__(*args, **kwargs)

        # Garante que o formato da data seja interpretado corretamente
        self.fields['data_inicio'].input_formats = ['%Y-%m-%d']     
        self.fields['data_fim'].input_formats = ['%Y-%m-%d']   

        # Remove o campo nome se estiver editando
        if modo_edicao:
            self.fields.pop('nome', None)
            
            
        # 🔻 Remover temporariamente opções não utilizadas
        opcoes_excluidas = ['seguro_tainha', 'seguro_camarao']
        self.fields['nome'].choices = [
            choice for choice in self.fields['nome'].choices
            if choice[0] not in opcoes_excluidas
        ]    
      