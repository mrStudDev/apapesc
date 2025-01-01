from django.shortcuts import render
from .models import ArticlesModel, CategoryArticlesModel, TagArticlesModel
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from .forms import ArticleCreateForm, CategoryArticlesForm, TagArticlesForm
from django.urls import reverse_lazy
from django.utils.text import slugify

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



# Create your views here.
class ArticlesListView(ListView):
    model = ArticlesModel
    template_name = 'app_articles/list_articles.html'
    ordering = ['-date_created']
    paginate_by = 12
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["publicacoes_count"] = ArticlesModel.objects.all().count()

        return context

class ArticleSingleView(DetailView):
    model = ArticlesModel
    template_name = 'app_articles/single_article.html'
    slug_field = 'slug'
    reverse_lazy = reverse_lazy('article-delete-post')
    context_object_name = 'article'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategoryArticlesModel.objects.all()
        context['tags'] = TagArticlesModel.objects.all()

        return context


class ArticleCreateView(CreateView):
    model = ArticlesModel
    form_class = ArticleCreateForm
    template_name = 'app_articles/create_article.html'
    success_url = reverse_lazy('app_articles:list_articles')  # Substitua pelo nome correto do URL da lista de artigos

    def form_valid(self, form):
        # Defina o autor como o usuário logado
        form.instance.author = self.request.user
        return super().form_valid(form)


class EditArticleView(UpdateView):
    model = ArticlesModel
    form_class = ArticleCreateForm
    template_name = 'app_articles/edit_article.html'

    def get_success_url(self):
        # Redireciona para a página do artigo após edição
        return reverse('app_articles:single_article', kwargs={'slug': self.object.slug})

class DeleteArticleView(DeleteView):
    model = ArticlesModel
    template_name = 'app_articles/delete_article.html'
    success_url = reverse_lazy('app_articles:list_articles')
    
# Categorias
class CategoryCreateView(CreateView):
    model = CategoryArticlesModel
    form_class = CategoryArticlesForm
    template_name = 'app_articles/create_category.html'
    success_url = reverse_lazy('app_articles:list_categories')

    def form_valid(self, form):
        # Gera o slug com base no campo "name"
        form.instance.slug = slugify(form.cleaned_data['name'])
        return super().form_valid(form)

class CategoryEditView(UpdateView):
    model = CategoryArticlesModel
    form_class = CategoryArticlesForm
    template_name = 'app_articles/edit_category.html'
    success_url = reverse_lazy('app_articles:list_categories')

class CategoryDeleteView(DeleteView):
    model = CategoryArticlesModel
    template_name = 'app_articles/delete_category.html'
    success_url = reverse_lazy('app_articles:list_categories')  # Ajuste para a rota da lista de categorias
    success_message = "Categoria deletada com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.object
        return context
    
class CategoriesListView(ListView):
    template_name = 'app_articles/list_categories.html'
    ordering = ['-date_created']
    ordering = ['-id']  # Ordena por ID decrescente
    context_object_name = 'categories'
    paginate_by = 12 

    def get_queryset(self):
            # Retorna o conjunto de categorias ordenado
            return CategoryArticlesModel.objects.all().order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_count'] = CategoryArticlesModel.objects.count()  # Conta total de categorias
        return context
         
class CategoriesView(ListView):
    model = ArticlesModel
    template_name = 'app_articles/categories.html'
    context_object_name = 'articles'
    paginate_by = 12  # Paginação, opcional

    def get_queryset(self):
        # Filtra os artigos pela categoria selecionada
        slug = self.kwargs.get('slug')
        return ArticlesModel.objects.filter(category__slug=slug, is_published=True).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        # Obtem a categoria atual
        category = CategoryArticlesModel.objects.get(slug=slug)
        context['category'] = category
        # Contagem de artigos nesta categoria
        context['categories_count'] = ArticlesModel.objects.filter(category=category, is_published=True).count()
        return context


# Tags
class TagCreateView(CreateView):
    model = TagArticlesModel
    form_class = TagArticlesForm
    template_name = 'app_articles/create_tag.html'
    success_url = reverse_lazy('app_articles:list_tags')
    
    def form_valid(self, form):
        # Gera o slug com base no campo "name"
        form.instance.slug = slugify(form.cleaned_data['name'])
        return super().form_valid(form)

class TagEditView(UpdateView)    :
    model = TagArticlesModel
    form_class = TagArticlesForm
    template_name = 'app_articles/edit_tag.html'
    success_url = reverse_lazy('app_articles:list_tags')
    
class TagDeleteView(DeleteView):
    model = TagArticlesModel
    template_name = 'app_articles/delete_tag.html'
    success_url = reverse_lazy('app_articles:list_tags')
    success_message = "Categoria deletada com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = self.object
        return context
        
class TagsListView(ListView)    :
    template_name = 'app_articles/list_tags.html'
    ordering = ['-date_created']
    context_object_name = 'tags'
    ordering = ['-id']  # Ordena por ID decrescente
    context_object_name = 'tags'

    def get_queryset(self):
            # Retorna o conjunto de tagd ordenado
            return TagArticlesModel.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags_count"] = TagArticlesModel.objects.count()
        return context    
    
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