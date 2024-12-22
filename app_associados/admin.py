from django.contrib import admin
from .models import AssociadoModel, ProfissoesModel

@admin.register(AssociadoModel)
class AssociadoAdmin(admin.ModelAdmin):
    list_display = ['get_user_full_name', 'cpf', 'email', 'celular', 'data_atualizacao']
    list_filter = ['reparticao', 'associacao', 'status']
    search_fields = ['user__first_name', 'user__last_name', 'cpf', 'email', 'celular']

    def get_user_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else "Usuário não associado"
    get_user_full_name.short_description = 'Nome Completo'
    
    
@admin.register(ProfissoesModel)
class ProfissoesAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
