from django.contrib import admin
from .models import TipoDocumentoModel, Documento

@admin.register(TipoDocumentoModel)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo')  # Campos que aparecem na lista do admin
    search_fields = ('tipo',)  # Campos pesquisáveis
    ordering = ('tipo',)  # Ordenação padrão
    list_per_page = 20  # Paginação

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_doc', 'associado', 'integrante', 'data_upload')  # Campos que aparecem na lista do admin
    search_fields = ('tipo_doc__tipo', 'associado__user__first_name', 'associado__user__last_name', 'integrante__user__first_name', 'integrante__user__last_name')  # Campos pesquisáveis
    list_filter = ('tipo_doc', 'data_upload')  # Filtros laterais
    ordering = ('-data_upload',)  # Ordenação padrão (por data de upload decrescente)
    list_per_page = 20  # Paginação

    # Método opcional para exibir nome completo do associado/integrante
    def get_associado_nome(self, obj):
        return obj.associado.user.get_full_name() if obj.associado else None
    get_associado_nome.short_description = 'Nome do Associado'

    def get_integrante_nome(self, obj):
        return obj.integrante.user.get_full_name() if obj.integrante else None
    get_integrante_nome.short_description = 'Nome do Integrante'
