from django.urls import path
from . import views
from .views import (
    CreateAssociadoView,
    ListAssociadosView,
    SingleAssociadoView,
    EditAssociadoView,
    ListAssociadosAssociacaoView,
    ListAssociadosReparticaoView,
    CreateProfissaoView,
    EditProfissaoView,
    )

app_name = 'app_associados'

urlpatterns = [
    path('lista-geral/', ListAssociadosView.as_view(), name='list_geral_associado'),
    path('create/', CreateAssociadoView.as_view(), name='create_associado'),
    path('singular/<int:pk>/', SingleAssociadoView.as_view(), name='single_associado'),
    path('editar/<int:pk>/', EditAssociadoView.as_view(), name='edit_associado'),
    path('profissoes/criar/', CreateProfissaoView.as_view(), name='create_profissao'),
    path('profissoes/editar/<int:pk>/', EditProfissaoView.as_view(), name='edit_profissao'),
    #Filtros
    path('lista-por-associacao/', ListAssociadosAssociacaoView.as_view(), name='list_por_associacao'),
    path('lista-por-reparticao/', ListAssociadosReparticaoView.as_view(), name='list_por_reparticao'),
    #Filtros  Create Associado
    path('filtro-reparticoes/<int:associacao_id>/', views.filtro_reparticoes, name='filtro_reparticoes'),
    path('filtro-municipios/<int:reparticao_id>/', views.filtro_municipios, name='filtro_municipios'),
]