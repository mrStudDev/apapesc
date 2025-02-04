from django.shortcuts import render
from .models import ArticlesModel, CategoryArticlesModel, TagArticlesModel
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import GroupPermissionRequiredMixin

from .forms import (
    ArticleCreateForm,
    CategoryArticlesForm,
    TagArticlesForm
    )

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import (
    CategoryArticlesModel,
    TagArticlesModel,
    ArticlesModel,
)


# Artigos Lista - Acesso Livre
class ArticlesListView(ListView):
    model = ArticlesModel
    template_name = 'app_articles/list_articles.html'
    ordering = ['-date_created']
    paginate_by = 12
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["publicacoes_count"] = ArticlesModel.objects.all().count()
        context["categories"] = CategoryArticlesModel.objects.all()  # Inclua categorias
        return context

# Artigos Singular - Acesso Livre
class ArticleSingleView(DetailView):
    model = ArticlesModel
    template_name = 'app_articles/single_article.html'
    slug_field = 'slug'
    reverse_lazy = reverse_lazy('article-delete-post')
    context_object_name = 'article'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategoryArticlesModel.objects.exclude(slug__isnull=True).exclude(slug='')
        context['tags'] = TagArticlesModel.objects.all()

        return context

# Categorias Artigos  - Acesso livre Filtros
class CategoriesView(ListView):
    model = ArticlesModel
    template_name = 'app_articles/categories.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        if not slug:
            return ArticlesModel.objects.none()

        return ArticlesModel.objects.filter(
            category__slug=slug, is_published=True
        ).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        
        # Adiciona categoria ao contexto
        try:
            category = CategoryArticlesModel.objects.get(slug=slug)
            context['category'] = category
            context['categories_count'] = category.articles.filter(is_published=True).count()
        except CategoryArticlesModel.DoesNotExist:
            context['category'] = None
            context['categories_count'] = 0

        return context





# Tags Artigos - Acesso livre Filtros
class TagsView(ListView):
    model = ArticlesModel
    template_name = 'app_articles/tags.html'
    context_object_name = 'articles'
    paginate_by = 12  # Paginação, opcional

    def get_queryset(self):
        # Filtra os artigos pela categoria selecionada
        slug = self.kwargs.get('slug')
        return ArticlesModel.objects.filter(tags__slug=slug, is_published=True).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        tag = TagArticlesModel.objects.get(slug=slug)  # Obtém a tag pelo slug
        context['tags'] = tag  # Passa a tag para o contexto
        # Filtra e conta os artigos associados à tag
        context["tags_count"] = ArticlesModel.objects.filter(tags=tag, is_published=True).count()
        return context

    
#============ Acesso Restrito ============================== #
# Artigos Criar 
class ArticleCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = ArticlesModel
    form_class = ArticleCreateForm
    template_name = 'app_articles/create_article.html'
    success_url = reverse_lazy('app_articles:list_articles')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]  
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)
        
        response = super().form_valid(form)
        
        # Salva as tags depois que o artigo foi salvo
        form.instance.tags.set(form.cleaned_data['tags'])
        
        return response


class EditArticleView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = ArticlesModel
    form_class = ArticleCreateForm
    template_name = 'app_articles/edit_article.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]  
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Salva as tags após o artigo ser salvo
        form.instance.tags.set(form.cleaned_data['tags'])
        return response
        
    def get_success_url(self):
        # Redireciona para a página do artigo após edição
        return reverse('app_articles:single_article', kwargs={'slug': self.object.slug})


class DeleteArticleView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = ArticlesModel
    template_name = 'app_articles/delete_article.html'
    success_url = reverse_lazy('app_articles:list_articles')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]  
        
class CategoryCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = CategoryArticlesModel
    form_class = CategoryArticlesForm
    template_name = 'app_articles/create_category.html'
    success_url = reverse_lazy('app_articles:create_category')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
    ]

    def form_valid(self, form):
        # Gera o slug com base no campo "name"
        form.instance.slug = slugify(form.cleaned_data['name'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona todas as categorias ao contexto
        context['categories'] = CategoryArticlesModel.objects.all()
        return context


class CategoryEditView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = CategoryArticlesModel
    form_class = CategoryArticlesForm
    template_name = 'app_articles/edit_category.html'
    success_url = reverse_lazy('app_articles:create_category')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]  
    
class CategoryDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = CategoryArticlesModel
    template_name = 'app_articles/delete_category.html'
    success_url = reverse_lazy('app_articles:list_categories')  # Ajuste para a rota da lista de categorias
    success_message = "Categoria deletada com sucesso!"
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.object
        return context
    

# Tags
class TagCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = TagArticlesModel
    form_class = TagArticlesForm
    template_name = 'app_articles/create_tag.html'
    success_url = reverse_lazy('app_articles:create_tag')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
    ]

    def form_valid(self, form):
        # Gera o slug com base no campo "name"
        form.instance.slug = slugify(form.cleaned_data['name'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona todas as tags ao contexto
        context['tags'] = TagArticlesModel.objects.all()
        return context


class TagEditView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = TagArticlesModel
    form_class = TagArticlesForm
    template_name = 'app_articles/edit_tag.html'
    success_url = reverse_lazy('app_articles:create_tag')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]  
        
class TagDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = TagArticlesModel
    template_name = 'app_articles/delete_tag.html'
    success_url = reverse_lazy('app_articles:list_tags')
    success_message = "Categoria deletada com sucesso!"
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = self.object
        return context
        
