from django.contrib import admin
from .models import (
    DeclaracaoResidenciaModel,
    DeclaracaoFiliacaoModel,
    DeclaracaoAtividadePesqueiraModel,
    DeclaracaoHipossuficienciaModel,
    ProcuracaoJuridicaModel,
    )

@admin.register(DeclaracaoResidenciaModel)
class DeclaracaoResidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pdf_base', 'atualizado_em')  # Campos exibidos na lista do admin
    search_fields = ('pdf_base',)  # Campos de busca
    readonly_fields = ('atualizado_em',)  # Campos apenas leitura


@admin.register(DeclaracaoFiliacaoModel)
class DeclaracaoFiliacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pdf_base', 'atualizado_em')
    search_fields = ('pdf_base',)
    readonly_fields = ('atualizado_em',)
    
@admin.register(DeclaracaoAtividadePesqueiraModel)
class DeclaracaoAtividadePesqueiraAdmin(admin.ModelAdmin):
    list_display = ('id', 'pdf_base', 'atualizado_em')
    search_fields = ('pdf_base',)
    readonly_fields = ('atualizado_em',)

@admin.register(DeclaracaoHipossuficienciaModel)
class DeclaracaoHiposuficienciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pdf_base', 'atualizado_em')
    search_fields = ('pdf_base',)
    readonly_fields = ('atualizado_em',)

@admin.register(ProcuracaoJuridicaModel)
class ProcuracaoJuridicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pdf_base', 'atualizado_em')
    search_fields = ('pdf_base',)
    readonly_fields = ('atualizado_em',)