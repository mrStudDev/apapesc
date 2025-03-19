# app_finances/admin.py
from django.contrib import admin
from .models import AnuidadeModel
from .models import TipoDespesaModel, DespesaAssociacaoModel

@admin.register(AnuidadeModel)
class AnuidadeModelAdmin(admin.ModelAdmin):
    list_display = ('ano', 'valor_anuidade', 'data_criacao')
    list_filter = ('ano', 'data_criacao')
    search_fields = ('ano',)
    ordering = ('-ano',)
    date_hierarchy = 'data_criacao'
    fields = ('ano', 'valor_anuidade', 'data_criacao')
    readonly_fields = ('data_criacao',)

    def has_add_permission(self, request):
        """Evitar duplicidade para o mesmo ano."""
        if AnuidadeModel.objects.filter(ano=request.POST.get('ano')).exists():
            return False
        return super().has_add_permission(request)
    

@admin.register(TipoDespesaModel)
class TipoDespesaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(DespesaAssociacaoModel)
class DespesaAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'tipo_despesa', 'valor', 'data_vencimento', 'registrado_por')
    readonly_fields = ('data_lancamento', 'registrado_por', 'associacao')

    def save_model(self, request, obj, form, change):
        """Preenche automaticamente a associação e o usuário que está registrando."""
        if not obj.pk:
            # Busca a associação dinamicamente a partir do vínculo do usuário
            try:
                obj.associacao = request.user.integrante.associacao  # Certifique-se que o relacionamento está correto
            except AttributeError:
                raise ValueError("O usuário não está vinculado a uma associação válida.")

            obj.registrado_por = request.user
        super().save_model(request, obj, form, change)
