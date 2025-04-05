from django.contrib import admin
from django import forms
from .models import UsoCulinarioModel

class UsoCulinarioAdminForm(forms.ModelForm):
    class Meta:
        model = UsoCulinarioModel
        fields = '__all__'
        widgets = {
            'ingredientes': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': '• 500g de peixe\n• 1 colher de sal\n• Suco de 1 limão'
            }),
        }

class UsoCulinarioAdmin(admin.ModelAdmin):
    form = UsoCulinarioAdminForm
    list_display = ['nome_receita', 'especie', 'tipo', 'dificuldade']

admin.site.register(UsoCulinarioModel, UsoCulinarioAdmin)
