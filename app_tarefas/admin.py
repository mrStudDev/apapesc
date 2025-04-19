
# Register your models here.
from django.contrib import admin
from .models import TarefaModel, HistoricoStatusModel, HistoricoResponsaveisModel, LancamentoINSSModel, GuiaINSSModel

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


# === INSS ====

# === Inline das guias no lançamento ===
class GuiaINSSInline(admin.TabularInline):
    model = GuiaINSSModel
    extra = 0
    readonly_fields = ('associado', 'status', 'data_emissao')
    can_delete = False

# === Admin do Lançamento ===
# Inline das guias
class GuiaINSSInline(admin.TabularInline):
    model = GuiaINSSModel
    extra = 0
    readonly_fields = ('associado', 'status', 'data_emissao')

# === Admin do Lançamento ===
@admin.register(LancamentoINSSModel)
class LancamentoINSSAdmin(admin.ModelAdmin):
    list_display = ('ano', 'mes', 'criado_em', 'criado_por')
    list_filter = ('ano', 'mes',)
    search_fields = ('ano', 'mes')
    inlines = [GuiaINSSInline]
    ordering = ['-ano', '-mes']
    date_hierarchy = 'criado_em'

    def save_model(self, request, obj, form, change):
        """
        ⚠️ Este método é chamado sempre que um objeto é salvo no admin.
        Se for um novo objeto, vamos chamar o gerar_lancamento()
        """
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        if is_new:
            # ⚠️ Gera as guias assim que o lançamento for salvo
            LancamentoINSSModel.gerar_lancamento(obj.ano, obj.mes, request.user)

# === Admin separado para Guia (opcional) ===
@admin.register(GuiaINSSModel)
class GuiaINSSAdmin(admin.ModelAdmin):
    list_display = ('lancamento', 'associado', 'status', 'data_emissao')
    list_filter = ('status', 'lancamento__ano', 'lancamento__mes')
    search_fields = ('associado__user__first_name', 'associado__user__last_name')
    autocomplete_fields = ['associado', 'lancamento']
    readonly_fields = ('data_emissao',)
