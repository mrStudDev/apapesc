from django import forms
from app_finances.models import AnuidadeModel

class AnuidadeForm(forms.ModelForm):
    class Meta:
        model = AnuidadeModel
        fields = ['ano', 'valor_anuidade']
        widgets = {
            'ano': forms.NumberInput(attrs={
                'placeholder': 'Digite o Ano (Ex: 2025)',
                'class': 'border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm'
            }),
            'valor_anuidade': forms.TextInput(attrs={
                'placeholder': 'Valor da Anuidade (Ex: 250.00) Use o ponto para separar os centavos.',
                'class': 'border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm'
            })
        }
