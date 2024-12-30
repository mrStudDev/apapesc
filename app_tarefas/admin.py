
# Register your models here.
from django.contrib import admin
from .models import TarefaModel, HistoricoStatusModel, HistoricoResponsaveisModel

@admin.register(TarefaModel)
class TarefaModelAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'data_criacao', 'data_limite', 'criado_por')
    search_fields = ('titulo', 'descricao', 'criado_por__username')
    list_filter = ('status', 'data_criacao', 'data_limite')
    ordering = ('-data_criacao',)
    prepopulated_fields = {'slug': ('titulo',)} 

@admin.register(HistoricoStatusModel)
class HistoricoStatusModelAdmin(admin.ModelAdmin):
    list_display = ('tarefa', 'status_anterior', 'status_novo', 'alterado_por', 'data_alteracao')
    search_fields = ('tarefa__titulo', 'alterado_por__user__username')
    list_filter = ('status_anterior', 'status_novo', 'data_alteracao')
    ordering = ('-data_alteracao',)

@admin.register(HistoricoResponsaveisModel)
class HistoricoResponsaveisAdmin(admin.ModelAdmin):
    list_display = ('tarefa', 'get_responsaveis_anteriores', 'get_responsaveis_novos', 'alterado_por', 'data_alteracao')
    search_fields = ('tarefa__titulo', 'alterado_por__user__username')
    list_filter = ('data_alteracao',)
    ordering = ('-data_alteracao',)

    def get_responsaveis_anteriores(self, obj):
        # Retorna uma string com os nomes dos responsáveis anteriores
        return ", ".join([responsavel.user.get_full_name() for responsavel in obj.responsaveis_anteriores.all()])
    get_responsaveis_anteriores.short_description = 'Responsáveis Anteriores'

    def get_responsaveis_novos(self, obj):
        # Retorna uma string com os nomes dos novos responsáveis
        return ", ".join([responsavel.user.get_full_name() for responsavel in obj.responsaveis_novos.all()])
    get_responsaveis_novos.short_description = 'Responsáveis Novos'

