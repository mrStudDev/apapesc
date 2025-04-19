from django.urls import path
from . import views
from .views import (
    AssociacaoListView, 
    AssociacaoDetailView,
    AssociacaoCreateView,
    AssociacaoUpdateView,
    AssociacaoDeleteView,
    IntegrantesListView,
    IntegrantesDetailView,
    IntegrantesCreateView,
    IntegrantesUpdateView,
    IntegrantesDeleteView,
    MunicipiosListView,
    MunicipiosDetailView,
    MunicipiosCreateView,
    MunicipiosUpdateView,
    MunicipiosDeleteView,
    ReparticoesListView,
    ReparticoesDetailView,
    ReparticoesCreateView,
    ReparticoesUpdateView,
    ReparticoesDeleteView,
    UserListView,
    ExIntegrantesListView,
    CargoscListView,
    CargoDetailView,
    CargoUpdateView,
    CargoDeleteView,
    CargoCreateView,
)

# App Space Name
app_name = 'app_associacao'

urlpatterns = [
    # AssociaçãoURLs
    path('associacao/', AssociacaoListView.as_view(), name='list_associacao'),
    path('associacao/create/', AssociacaoCreateView.as_view(), name='create_associacao'),
    path('associacao/<int:pk>/', AssociacaoDetailView.as_view(), name='single_associacao'),
    path('associacao/<int:pk>/edit/', AssociacaoUpdateView.as_view(), name='edit_associacao'),
    path('associacao/<int:pk>/delete/', AssociacaoDeleteView.as_view(), name='delete_associacao'),

    # Integrantes URLs
    path('integrantes/', IntegrantesListView.as_view(), name='list_integrante'),
    path('integrantes/create/', IntegrantesCreateView.as_view(), name='create_integrante'),
    path('integrantes/<int:pk>/', IntegrantesDetailView.as_view(), name='single_integrante'),
    path('integrantes/<int:pk>/edit/', IntegrantesUpdateView.as_view(), name='edit_integrante'),
    path('integrantes/<int:pk>/delete/', IntegrantesDeleteView.as_view(), name='delete_integrante'),
    
    path('ex-integrantes/', ExIntegrantesListView.as_view(), name='ex_integrantes'),
    
    # Cargos URLs
    path('cargos/', CargoscListView.as_view(), name='list_cargo'),
    path('cargos/create/', CargoCreateView.as_view(), name='create_cargo'),
    path('cargos/<int:pk>/', CargoDetailView.as_view(), name='single_cargo'),
    path('cargos/<int:pk>/edit/', CargoUpdateView.as_view(), name='edit_cargo'),
    path('cargos/<int:pk>/delete/', CargoDeleteView.as_view(), name='delete_cargo'),

    # Municipios URLs
    path('municipios/', MunicipiosListView.as_view(), name='list_municipio'),
    path('municipios/create/', MunicipiosCreateView.as_view(), name='create_municipio'),
    path('municipios/<int:pk>/', MunicipiosDetailView.as_view(), name='single_municipio'),
    path('municipios/<int:pk>/edit/', MunicipiosUpdateView.as_view(), name='edit_municipio'),
    path('municipios/<int:pk>/delete/', MunicipiosDeleteView.as_view(), name='delete_municipio'),

    # Reparticoes URLs
    path('reparticoes/', ReparticoesListView.as_view(), name='list_reparticao'),
    path('reparticoes/create/', ReparticoesCreateView.as_view(), name='create_reparticao'),
    path('reparticoes/<int:pk>/', ReparticoesDetailView.as_view(), name='single_reparticao'),
    path('reparticoes/<int:pk>/edit/', ReparticoesUpdateView.as_view(), name='edit_reparticao'),
    path('reparticoes/<int:pk>/delete/', ReparticoesDeleteView.as_view(), name='delete_reparticao'),


    path('users/', UserListView.as_view(), name='list_users'),
    path('reintegrate-integrante/', views.reintegrate_integrante, name='reintegration_integrante'),
    path('reassociar/', views.reassociar_associado, name='reassociar_associado'),

]