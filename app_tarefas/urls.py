from django.urls import path
from . import views

from .views import (
    TarefaCreateView,
    TarefaListView,
    TarefaDetailView,
    TarefaEditView,
    TarefaBoardView,
    TarefaArquivadaListView,
    TarefaDeleteView,

    )


app_name = 'app_tarefas'

urlpatterns = [
    path('lista-tarefas/', TarefaListView.as_view(), name='list_tarefas'),
    path('criar-tarefa/', TarefaCreateView.as_view(), name='create_tarefa'),
    path('editar-tarefa/<int:pk>/', TarefaEditView.as_view(), name='edit_tarefa'),
    path('single/<int:pk>/', TarefaDetailView.as_view(), name='single_tarefa'),
    
    path('starus/<int:pk>/alterar-status/', views.alterar_status_tarefa, name='alterar_status'),
    path('responsaveis/<int:pk>/alterar-responsaveis/', views.alterar_responsaveis_tarefa, name='alterar_responsaveis'),
    
    path('board/', TarefaBoardView.as_view(), name='board_tarefas'),
    path('board/<int:pk>/alterar-status-board/', views.alterar_status_tarefa_board, name='alterar_status_tarefa_board'),

    path('arquivadas/', TarefaArquivadaListView.as_view(), name='tarefas_arquivadas'),
    path('arquivar/<int:pk>/', views.arquivar_tarefa, name='arquivar_tarefa'),
    path('desarquivar/<int:pk>/', views.desarquivar_tarefa, name='desarquivar_tarefa'),
    path('deletar/<int:pk>/', TarefaDeleteView.as_view(), name='deletar_tarefa'),
    
]

