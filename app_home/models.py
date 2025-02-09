from django.db import models
from django.core.validators import RegexValidator
# Create your models here.

class HomeModel(models.Model):
    pass

class LeadInformacoes(models.Model):
    nome = models.CharField(max_length=100)
    celular = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                r'^\(\d{2}\)\d{5}-\d{4}$',  # Garante que o número seja no formato (XX)XXXXX-XXXX
                'Número inválido. O telefone deve conter 10 ou 11 dígitos, ex: (48)99999-9999.'
            )
        ]
    ) 
    email = models.EmailField(blank=True)
    mensagem = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Lead Informações"
        
# Contato
class ContactMessagesModel(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.subject