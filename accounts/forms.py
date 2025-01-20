from django.utils.module_loading import import_string
from django import forms
from allauth.account.forms import LoginForm

# Carregando a classe SignupForm de forma segura
SignupForm = import_string("allauth.account.forms.SignupForm")

class CustomSignupForm(SignupForm):
    username = forms.CharField(max_length=30, required=True, label="Nome de Usuário")
    first_name = forms.CharField(max_length=30, required=True, label="Nome")
    last_name = forms.CharField(max_length=30, required=True, label="Sobrenome")

    def save(self, request):
        # Salva o usuário usando o método do SignupForm original
        user = super(CustomSignupForm, self).save(request)
        user.username = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        return user
                           
class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalize os campos
        self.fields['login'].widget.attrs.update({
            'placeholder': 'Digite seu email ou nome de usuário',
            'class': 'w-full border border-gray-300 rounded-md py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Digite sua senha',
            'class': 'w-full border border-gray-300 rounded-md py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        })