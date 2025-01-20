from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import LeadInformacoes
from .models import ContactMessagesModel


class LeadInformacoesForm(forms.ModelForm):
    class Meta:
        model = LeadInformacoes
        fields = ['nome', 'celular', 'email', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Digite o seu Nome',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),
            'celular': forms.TextInput(attrs={
                'placeholder': '(99)99999-9999',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraTelefone(this)',  # Chama a função de máscara para celular
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemplo@email.com',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-blue-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),            
            'mensagem': forms.Textarea(attrs={
                'placeholder': 'Sua mensagem... Sua Dúvida...',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm',
                'rows': 3,

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
    

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessagesModel
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Digite o seu Nome',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemplo@email.com',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-blue-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),             

            'subject': forms.Textarea(attrs={
                'placeholder': 'Assunto',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm',
                'rows': 3,
            }),           
            'message': forms.Textarea(attrs={
                'placeholder': 'Sua mensagem... Sua Dúvida...',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm',
                'rows': 3,
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nome'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['subject'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Assunto'})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Menssagem'})