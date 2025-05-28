from django.urls import path
from . import views
from .views import (
    PainelBeneficiosView,
    AdicionarBeneficioView,
    BeneficioListView,
    ListaBeneficiosView,
    ControleBeneficioDetailView,
    ListaEditaBeneficiosView,
    ProcessarLevaItemView,
)
app_name = 'app_beneficios'

urlpatterns = [
    # Bebeficios Cadastrados
    path('todos/', BeneficioListView.as_view(), name='beneficios'), 
    
    # Lista de Beneficios - Controle - listagem
    path('lista-beneficios/', ListaBeneficiosView.as_view(), name='lista_beneficios'), 
    
    # Controle Detalhe - detalhes do beneficio/dados Associado
    path('controle/<int:pk>/', ControleBeneficioDetailView.as_view(), name='controle_detalhe'),
    
    path('aplicar-beneficios/<int:associado_id>/', views.aplicar_beneficios_para_associado, name='aplicar_beneficios'),
    path('painel-beneficios/', PainelBeneficiosView.as_view(), name='painel_beneficios'),
    path('adicionar/', AdicionarBeneficioView.as_view(), name='create_beneficio'),
    
    # Leva de processamento de beneficios
    path('leva/processar/item/<int:item_id>/', ProcessarLevaItemView.as_view(), name='processar_item_leva'),
    path('leva/criar/<int:beneficio_id>/', views.criar_leva_view, name='criar_leva'),


    # Leva de processamento de beneficios   
    path('beneficios/', ListaEditaBeneficiosView.as_view(), name='lista_edita_beneficios'),


    
    path('deletar/<int:pk>/', views.deletar_beneficio, name='deletar_beneficio'),
]