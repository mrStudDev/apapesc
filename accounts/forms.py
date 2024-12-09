from django.utils.module_loading import import_string
from django import forms

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
                           