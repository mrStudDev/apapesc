from django.urls import path

from . views import (
  ArticlesListView, 
  ArticleSingleView,
  ArticleCreateView,
  EditArticleView,
  DeleteArticleView,
  CategoryCreateView,
  TagCreateView,
  CategoriesView,
  TagsView,
  TagEditView,
  CategoryEditView,
  CategoryDeleteView,
  TagDeleteView,

  )

app_name = 'app_articles'

urlpatterns = [
  path('', ArticlesListView.as_view(), name='list_articles'),
  path('post/<slug:slug>/', ArticleSingleView.as_view(), name='single_article'),
  path('create/', ArticleCreateView.as_view(), name='create_article'),
  path('edit/<slug:slug>/', EditArticleView.as_view(), name='edit_article'),
  path('delete/<slug:slug>/', DeleteArticleView.as_view(), name='delete_article'),
  
  path('create-category/', CategoryCreateView.as_view(), name='create_category'),  
  path('edit-categoria/<int:pk>/', CategoryEditView.as_view(), name='edit_category'),
  path('delete-categoria/<int:pk>/', CategoryDeleteView.as_view(), name='delete_category'),


  
  path('create-tag/', TagCreateView.as_view(), name='create_tag'),
  path('edit-tag/<int:pk>/', TagEditView.as_view(), name='edit_tag'),
  path('delete-tag/<int:pk>/', TagDeleteView.as_view(), name='delete_tag'),
  path('categoria/<slug:slug>/', CategoriesView.as_view(), name='category_articles'),
  path('tags-filtro/<slug:slug>/', TagsView.as_view(), name='tags_articles'),
  
]