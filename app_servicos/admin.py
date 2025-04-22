from django.contrib import admin
from .models import ServicoAssociadoModel, ServicoExtraAssociadoModel, ServicoHistoricoModel, ExtraAssociadoModel

@admin.register(ServicoAssociadoModel)
class ServicoAssociadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'associado', 'tipo_servico', 'status_etapa', 'data_inicio']
    list_filter = ['status_etapa', 'associacao']
    search_fields = ['descricao', 'associado__user__first_name', 'associado__user__last_name']

@admin.register(ServicoExtraAssociadoModel)
class ServicoExtraAdmin(admin.ModelAdmin):
    list_display = ['id', 'extra_associado', 'tipo_servico', 'status_etapa', 'data_inicio']
    list_filter = ['status_etapa', 'associacao']
    search_fields = ['descricao', 'extra_associado__nome_completo']

@admin.register(ServicoHistoricoModel)
class ServicoHistoricoAdmin(admin.ModelAdmin):
    list_display = ['campo', 'valor_antigo', 'valor_novo', 'alterado_por', 'data_alteracao']
    search_fields = ['campo', 'valor_antigo', 'valor_novo']

@admin.register(ExtraAssociadoModel)
class ExtraAssociadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome_completo', 'cpf', 'celular','senha_gov']
    search_fields = ['nome_completo', 'cpf']
    list_filter = ['nome_completo']
    ordering = ['nome_completo']
