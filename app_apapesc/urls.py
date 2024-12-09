from django.urls import path
from . import views
from .views import (
    ApapescListView, ApapescDetailView, ApapescCreateView, ApapescUpdateView, ApapescDeleteView,
    IntegrantesListView, IntegrantesDetailView, IntegrantesCreateView, IntegrantesUpdateView, IntegrantesDeleteView,
    MunicipiosListView, MunicipiosDetailView, MunicipiosCreateView, MunicipiosUpdateView, MunicipiosDeleteView,
    ReparticoesListView, ReparticoesDetailView, ReparticoesCreateView, ReparticoesUpdateView, ReparticoesDeleteView,
    UserListView, ExIntegrantesListView,
)

app_name = 'app_apapesc'

urlpatterns = [
    # Apapesc URLs
    path('apapesc/', ApapescListView.as_view(), name='list_apapesc'),
    path('apapesc/create/', ApapescCreateView.as_view(), name='create_apapesc'),
    path('apapesc/<int:pk>/', ApapescDetailView.as_view(), name='single_apapesc'),
    path('apapesc/<int:pk>/edit/', ApapescUpdateView.as_view(), name='edit_apapesc'),
    path('apapesc/<int:pk>/delete/', ApapescDeleteView.as_view(), name='delete_apapesc'),

    # Integrantes URLs
    path('integrantes/', IntegrantesListView.as_view(), name='list_integrante'),
    path('integrantes/create/', IntegrantesCreateView.as_view(), name='create_integrante'),
    path('integrantes/<int:pk>/', IntegrantesDetailView.as_view(), name='single_integrante'),
    path('integrantes/<int:pk>/edit/', IntegrantesUpdateView.as_view(), name='edit_integrante'),
    path('integrantes/<int:pk>/delete/', IntegrantesDeleteView.as_view(), name='delete_integrante'),
    
    path('ex-integrantes/', ExIntegrantesListView.as_view(), name='ex_integrantes'),

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
]