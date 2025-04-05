from django.contrib import admin
from django import forms
from .models import (
    ReinoModel,
    FiloModel,
    GrupoBiologicoModel,
    EspecieMarinhaModel,
    ReferenciaBibliograficaModel,
    RegiaoGeograficaModel,
    DistribuicaoGeograficaModel,
    StatusConservacaoModel,
    ImagemEspecieModel,
    NomeComumModel,
    HabitatModel,
    TipoAmeacaModel,
    AmeacaModel,
    UsoCulinarioModel
)

# 🧠 Base para modelos simples com slug
class SlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nome",)}
    search_fields = ("nome",)

# 🌱 Taxonomia
@admin.register(ReinoModel)
class ReinoAdmin(SlugAdmin):
    list_display = ("nome",)
    
@admin.register(FiloModel)
class FiloAdmin(SlugAdmin):
    list_display = ("nome", "reino")
    list_filter = ("reino",)
    autocomplete_fields = ("reino",)

@admin.register(GrupoBiologicoModel)
class GrupoBiologicoAdmin(SlugAdmin):
    list_display = ("nome",)

# 🐚 Espécie
@admin.register(EspecieMarinhaModel)
class EspecieMarinhaAdmin(admin.ModelAdmin):
    list_display = ("nome_cientifico", "nome_comum", "reino", "filo", "validado")
    search_fields = ("nome_cientifico", "nome_comum")
    list_filter = ("reino", "filo", "grupo_biologico", "validado")
    autocomplete_fields = ("reino", "filo", "grupo_biologico", "especies_relacionadas", "habitat")
    readonly_fields = ("data_cadastro", "data_ultima_alteracao")
    prepopulated_fields = {"slug": ("nome_cientifico",)}

# 📚 Referência
@admin.register(ReferenciaBibliograficaModel)
class ReferenciaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "especie", "autor", "ano")
    search_fields = ("titulo", "autor")
    list_filter = ("ano",)
    autocomplete_fields = ("especie",)

# 🗺️ Regiões e distribuição
@admin.register(RegiaoGeograficaModel)
class RegiaoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)

@admin.register(DistribuicaoGeograficaModel)
class DistribuicaoAdmin(admin.ModelAdmin):
    list_display = ("especie", "regiao", "detalhes")
    autocomplete_fields = ("especie", "regiao")

# 🚨 Status de conservação
@admin.register(StatusConservacaoModel)
class StatusConservacaoAdmin(admin.ModelAdmin):
    list_display = ("especie", "sistema", "status", "ano_avaliacao")
    list_filter = ("sistema", "status", "ano_avaliacao")
    autocomplete_fields = ("especie",)

# 🖼️ Imagens
@admin.register(ImagemEspecieModel)
class ImagemAdmin(admin.ModelAdmin):
    list_display = ("especie", "descricao")
    search_fields = ("descricao",)
    autocomplete_fields = ("especie",)

# 🗣️ Nome comum
@admin.register(NomeComumModel)
class NomeComumAdmin(admin.ModelAdmin):
    list_display = ("nome", "especie", "idioma", "regiao")
    search_fields = ("nome",)
    list_filter = ("idioma",)
    autocomplete_fields = ("especie",)

# 🧭 Habitat
@admin.register(HabitatModel)
class HabitatAdmin(admin.ModelAdmin):
    list_display = ("id", "nome",)
    search_fields = ("nome",)

# ⚠️ Ameaças
@admin.register(TipoAmeacaModel)
class TipoAmeacaAdmin(SlugAdmin):
    list_display = ("nome",)

@admin.register(AmeacaModel)
class AmeacaAdmin(admin.ModelAdmin):
    list_display = ("especie", "tipo", "gravidade")
    list_filter = ("gravidade",)
    autocomplete_fields = ("especie", "tipo")
    prepopulated_fields = {"slug": ("tipo",)}  # ❗ Se você quiser usar "tipo" como slug base

# 🍽️ Uso culinário
class UsoCulinarioAdminForm(forms.ModelForm):
    class Meta:
        model = UsoCulinarioModel
        fields = '__all__'
        widgets = {
            'ingredientes': forms.Textarea(attrs={
                'rows': 6,
                'style': 'font-family: monospace;',
                'placeholder': '• 1kg de peixe\n• Suco de 2 limões\n• Sal e alho a gosto',
            }),
            'modo_preparo': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Descreva o passo a passo...',
            }),
            'dicas': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Dica: Sirva com arroz de coco...',
            }),
        }

class UsoCulinarioAdmin(admin.ModelAdmin):
    form = UsoCulinarioAdminForm
    list_display = ['nome_receita', 'especie', 'tipo', 'dificuldade']
    search_fields = ['nome_receita', 'especie__nome_comum']
    list_filter = ['tipo', 'dificuldade']

admin.site.register(UsoCulinarioModel, UsoCulinarioAdmin)
