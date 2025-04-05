from django.urls import path
from . import views

from .views import (
    CreateServicoAssociadoView,
    CreateServicoExtraAssociadoView,
    CreateExtraAssociadoView,
    ListServicosView,
    SingleServicoView,
    ListExtraAssociadosView,
    DetailExtraAssociadoView,
    ServicoExtraDetailView,
    EditServicoExtraAssociadoView,
    EditServicoAssociadoView,
    PainelServicosEtapasView,
    EditExtraAssociadoView
    
    )

app_name = 'app_servicos'

urlpatterns = [
    # Extra Associado Cadastro
    path('extraassociado/novo/', CreateExtraAssociadoView.as_view(), name='create_extraassociado'),    
    path('extraassociado/<int:pk>/', DetailExtraAssociadoView.as_view(), name='detail_extraassociado'), 
    path('extraassociados/', ListExtraAssociadosView.as_view(), name='list_extraassociados'), 
    path('extraassociado/<int:pk>/editar/', EditExtraAssociadoView.as_view(), name='edit_extraassociado'), 
    
       
    # Serviço Associado
    path('novo/associado/<int:associado_id>/', CreateServicoAssociadoView.as_view(), name='create_servico_associado'),
    path('editar/associado/<int:pk>/', EditServicoAssociadoView.as_view(), name='edit_servico_associado'),    
    path('servico/<int:pk>/', SingleServicoView.as_view(), name='single_servico'), # Serviço Singular Assocido
    
    # Serviço Extra Associado
    path('novo/extraassociado/<int:extra_id>/', CreateServicoExtraAssociadoView.as_view(), name='create_servico_extra'),    
    path('servicos/extra/<int:pk>/editar/', EditServicoExtraAssociadoView.as_view(), name='edit_servico_extra'),    
    path('servicos/extra/<int:pk>/', ServicoExtraDetailView.as_view(), name='single_servico_extra'),# Serviço Singular Extra-Assocido

    # Lista geral de Serviços
    path('servicos/', ListServicosView.as_view(), name='list_servicos'),
    
    # Painel de Etapas
    path('painel/etapas/', PainelServicosEtapasView.as_view(), name='painel_etapas'),    
    
    # Funções
    path('ajax/reparticoes/', views.carregar_reparticoes, name='ajax_carregar_reparticoes'),
    

]
