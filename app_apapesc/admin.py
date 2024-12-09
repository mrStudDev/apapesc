from django.contrib import admin

from .models import (
    ApapescModel,
    IntegrantesModel,
    CargosModel,
    ReparticoesModel,
    MunicipiosModel
    )


@admin.register(ApapescModel)
class ApapescAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'razao_social', 'cnpj')
    search_fields = ['nome_fantasia', 'razao_social', 'cnpj']

@admin.register(IntegrantesModel)
class IntegrantesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cargo', 'data_entrada')
    search_fields = ['user__email', 'cargo__nome']

@admin.register(CargosModel)
class CargosAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ['nome',]

@admin.register(ReparticoesModel)
class ReparticoesAdmin(admin.ModelAdmin):
    list_display = ('nome_reparticao', 'municipio_sede', 'delegado')
    search_fields = ['nome_reparticao', 'municipio_sede']

@admin.register(MunicipiosModel)
class MunicipiosAdmin(admin.ModelAdmin):
    list_display = ('municipio', 'uf',)
    search_fields = ['municipio', 'uf',]

