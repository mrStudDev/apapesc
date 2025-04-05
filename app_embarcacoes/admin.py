# app_embarcacoes/admin.py
from django.contrib import admin
from .models import EmbarcacoesModel, TipoEmbarcacaoModel, TipoPropulsaoModel


@admin.register(EmbarcacoesModel)
class EmbarcacoesAdmin(admin.ModelAdmin):
    list_display = ('nome_embarcacao', 'proprietario', 'inscricao_embarcacao', 'validade_tie', 'tipo_embarcacao')
    list_filter = ('tipo_embarcacao', 'tipo_propulsao', 'combustivel', 'alienacao')
    search_fields = ('nome_embarcacao', 'inscricao_embarcacao', 'proprietario__user__first_name', 'proprietario__user__last_name')
    autocomplete_fields = ['proprietario', 'tipo_embarcacao', 'tipo_propulsao']
    readonly_fields = ('data_atualizacao',)
    ordering = ['nome_embarcacao']


@admin.register(TipoEmbarcacaoModel)
class TipoEmbarcacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


@admin.register(TipoPropulsaoModel)
class TipoPropulsaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
