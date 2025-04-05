from django import forms
from .models import LicencasModel


class LicencaForm(forms.ModelForm):
    class Meta:
        model = LicencasModel
        exclude = ['data_alteracao']
        fields = '__all__'
        widgets = {
            'embarcacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
            }),
            'orgao_nome': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
            }),
            'licenca_nome': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
            }),
            'num_processo': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Número do processo'
            }),
            'num_atoAdmConcede': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Número do ato administrativo'
            }),
            'codigo_frota': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Código da frota'
            }),
            'inscricao_aut_naval': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Inscrição/autorização naval'
            }),
            'modalidade_permissionamento': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'placeholder': 'Modalidade de permissionamento'
            }),
            'validade_inicial': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
                },
                format='%Y-%m-%d'
            ),
            'validade_final': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700'
                },
                format='%Y-%m-%d'
            ),
            'content': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
                'rows': 4,
                'placeholder': 'Observações ou anotações adicionais'
            }),
        }
        
    def __init__(self, *args, embarcacao=None, **kwargs):
        super().__init__(*args, **kwargs)

        if embarcacao:
            self.fields['embarcacao'].initial = embarcacao
            self.fields['embarcacao'].widget = forms.HiddenInput()
