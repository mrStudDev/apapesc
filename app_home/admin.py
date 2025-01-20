from django.contrib import admin
from .models import LeadInformacoes, ContactMessagesModel

@admin.register(ContactMessagesModel)
class ContactMessagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')  # Colunas exibidas no Django Admin
    list_filter = ('created_at',)  # Filtro lateral por data de criação
    search_fields = ('name', 'email', 'subject', 'message')  # Campos pesquisáveis
    ordering = ('-created_at',)  # Ordenação padrão (mais recente primeiro)
    date_hierarchy = 'created_at' 

@admin.register(LeadInformacoes)
class LeadInformacoesAdmin(admin.ModelAdmin):
    list_display = ('nome', 'celular', 'email', 'created_at')
    search_fields = ('nome', 'celular', 'email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)  # Ordenação por data mais recente

