from django.urls import path
from . import views
from .views import PainelBeneficiosView, AdicionarBeneficioView, BeneficioListView # Import the missing view

app_name = 'app_beneficios'

urlpatterns = [
    path('lista/', views.lista_beneficios, name='lista_beneficios'),
    path('controle/<int:pk>/', views.controle_beneficio_detail, name='controle_detalhe'),
    path('aplicar-beneficios/<int:associado_id>/', views.aplicar_beneficios_para_associado, name='aplicar_beneficios'),
    path('painel-beneficios/', PainelBeneficiosView.as_view(), name='painel_beneficios'),
    path('adicionar/', AdicionarBeneficioView.as_view(), name='create_beneficio'),
    path('gerenciar/', views.lista_e_edita_beneficios, name='lista_edita_beneficios'),
    path('todos/', BeneficioListView.as_view(), name='beneficios'),
    path('deletar/<int:pk>/', views.deletar_beneficio, name='deletar_beneficio'),
]