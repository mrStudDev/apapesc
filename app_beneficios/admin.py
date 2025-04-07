from django.contrib import admin
from .models import BeneficioModel, ControleBeneficioModel, ControleBeneficioHistoricoModel
from django.urls import reverse
from django.utils.html import format_html


# 🔹 Inline para histórico
class HistoricoInline(admin.TabularInline):
    model = ControleBeneficioHistoricoModel
    extra = 0
    readonly_fields = ['alterado_em', 'alterado_por', 'campo_alterado', 'valor_anterior', 'valor_novo']
    can_delete = False
    verbose_name_plural = "Histórico de Alterações"


# 🔹 Admin do Controle
@admin.register(ControleBeneficioModel)
class ControleBeneficioAdmin(admin.ModelAdmin):
    list_display = ['associado', 'beneficio_nome', 'beneficio_ano', 'beneficio_estado', 'status_pedido', 'data_entrada']
    list_filter = ['status_pedido', 'beneficio__nome', 'beneficio__ano_concessao', 'beneficio__estado']
    search_fields = ['associado__user__first_name', 'associado__user__last_name', 'numero_protocolo']
    inlines = [HistoricoInline]
    readonly_fields = ['criado_em', 'atualizado_em']
    
    def beneficio_nome(self, obj):
        return obj.beneficio.get_nome_display()
    
    def beneficio_ano(self, obj):
        return obj.beneficio.ano_concessao
    
    def beneficio_estado(self, obj):
        return obj.beneficio.estado

    beneficio_nome.short_description = "Benefício"
    beneficio_ano.short_description = "Ano"
    beneficio_estado.short_description = "UF"


# 🔹 Admin do Benefício
@admin.register(BeneficioModel)
class BeneficioModelAdmin(admin.ModelAdmin):
    list_display = ['nome_display', 'ano_concessao', 'estado', 'data_inicio', 'data_fim', 'ver_beneficiarios']
    list_filter = ['nome', 'ano_concessao', 'estado']
    search_fields = ['lei_federal', 'instrucao_normativa', 'portaria']

    def nome_display(self, obj):
        return obj.get_nome_display()
    nome_display.short_description = "Benefício"

    # Removed redundant imports
    from django.urls import reverse

    def ver_beneficiarios(self, obj):
        url = reverse("admin:app_beneficios_controlebeneficiomodel_changelist")
        query = f"?beneficio__id__exact={obj.id}"
        return format_html('<a href="{}{}">📄 Ver Beneficiários</a>', url, query)
    ver_beneficiarios.short_description = "Controles"


# 🔹 Admin do histórico (visualização opcional direta)
@admin.register(ControleBeneficioHistoricoModel)
class ControleBeneficioHistoricoAdmin(admin.ModelAdmin):
    list_display = ['controle', 'campo_alterado', 'valor_anterior', 'valor_novo', 'alterado_em', 'alterado_por']
    list_filter = ['campo_alterado', 'alterado_em']
    search_fields = ['controle__associado__user__first_name', 'campo_alterado']
    readonly_fields = ['controle', 'alterado_em', 'alterado_por', 'campo_alterado', 'valor_anterior', 'valor_novo']
