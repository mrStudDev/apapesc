from django import forms
from .models import NotasApapescModel

class NotaForm(forms.ModelForm):
    class Meta:
        model = NotasApapescModel
        fields = ['titulo', 'content']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Digite o título da nota',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Digite o conteúdo aqui...',
                'class': 'border border-gray-300 rounded-md w-full p-3 h-40 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'id': 'editor',  # Define o ID para associar ao editor de texto
            }),
        }


