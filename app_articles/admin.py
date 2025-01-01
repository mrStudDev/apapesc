from django.contrib import admin
from .models import CategoryArticlesModel, TagArticlesModel, ArticlesModel


@admin.register(CategoryArticlesModel)
class CategoryArticlesAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}  # Preenche automaticamente o slug a partir do nome


@admin.register(TagArticlesModel)
class TagArticlesAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}  # Preenche automaticamente o slug a partir do nome


@admin.register(ArticlesModel)
class ArticlesAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'date_created', 'is_published', 'is_vip', 'code', 'slug')
    list_filter = ('is_published', 'category', 'tags', 'date_created')
    search_fields = ('title', 'author__username', 'keywords', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}  # Preenche automaticamente o slug a partir do título
    readonly_fields = ('date_created', 'last_updated', 'code')  # Campos somente leitura no admin
    filter_horizontal = ('tags',)  # Interface amigável para selecionar tags relacionadas
