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
    LancamentoINSSListView,
    GerarLancamentoINSSView,    
    DetalheLancamentoINSSView,
    ProcessarGuiaView,
    CriarLancamentoINSSView,
    )


app_name = 'app_tarefas'

urlpatterns = [
    path('lista-tarefas/', TarefaListView.as_view(), name='list_tarefas'),
    path('criar-tarefa/', TarefaCreateView.as_view(), name='create_tarefa'),
    path('create-tarefa/<int:associado_id>/', views.TarefaCreateView.as_view(), name='create_tarefa_associado'),
    path('editar-tarefa/<int:pk>/', TarefaEditView.as_view(), name='edit_tarefa'),
    path('single/<int:pk>/', TarefaDetailView.as_view(), name='single_tarefa'),
    
    # Guias INSS
    path('lancamento/', LancamentoINSSListView.as_view(), name='list_lancamentos'),
    path('tarefas/lancamento/gerar/', GerarLancamentoINSSView.as_view(), name='gerar_lancamento_inss'),
    path('inss/lancamento/<int:pk>/', DetalheLancamentoINSSView.as_view(), name='detalhe_lancamento_inss'),
    path('inss/guias/<int:guia_id>/atualizar/', views.atualizar_guia, name='atualizar_guia'),
    path('inss/lancamento/<int:lancamento_id>/processar/', ProcessarGuiaView.as_view(), name='processar_guia'),
    path('lancamento/novo/', CriarLancamentoINSSView.as_view(), name='create_lancamentoInss'),




    path('starus/<int:pk>/alterar-status/', views.alterar_status_tarefa, name='alterar_status'),
    path('responsaveis/<int:pk>/alterar-responsaveis/', views.alterar_responsaveis_tarefa, name='alterar_responsaveis'),
    
    path('board/', TarefaBoardView.as_view(), name='board_tarefas'),
    path('board/<int:pk>/alterar-status-board/', views.alterar_status_tarefa_board, name='alterar_status_tarefa_board'),

    path('arquivadas/', TarefaArquivadaListView.as_view(), name='tarefas_arquivadas'),
    path('arquivar/<int:pk>/', views.arquivar_tarefa, name='arquivar_tarefa'),
    path('desarquivar/<int:pk>/', views.desarquivar_tarefa, name='desarquivar_tarefa'),
    path('deletar/<int:pk>/', TarefaDeleteView.as_view(), name='deletar_tarefa'),
    
]


