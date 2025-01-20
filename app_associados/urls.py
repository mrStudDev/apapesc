from django.urls import path

from .views import (
    CreateAssociadoView,
    ListAssociadosView,
    SingleAssociadoView,
    EditAssociadoView,
    ListAssociadosAssociacaoView,
    ListAssociadosReparticaoView,
    )

app_name = 'app_associados'

urlpatterns = [
    path('lista-geral/', ListAssociadosView.as_view(), name='list_geral_associado'),
    path('create/', CreateAssociadoView.as_view(), name='create_associado'),
    path('singular/<int:pk>/', SingleAssociadoView.as_view(), name='single_associado'),
    path('editar/<int:pk>/', EditAssociadoView.as_view(), name='edit_associado'),
    
    #Filtros
    path('lista-por-associacao/', ListAssociadosAssociacaoView.as_view(), name='list_por_associacao'),
    path('lista-por-reparticao/', ListAssociadosReparticaoView.as_view(), name='list_por_reparticao'),
]
