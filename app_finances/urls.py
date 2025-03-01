from django.urls import path
from app_finances import views

from .views import (
    FinanceiroAssociadoDetailView,
    DarBaixaAnuidadeView,
    ResumoFinanceiroView,
    ListDespesasView,
    CreateAnuidadeView,
    EditAnuidadeView,
    DescontosAnuidadesView,
    )


app_name = 'app_finances'

urlpatterns = [
    path('anuidades/', views.lista_anuidades, name='list_anuidades'),
    path('financeiro/associado/<int:pk>/', FinanceiroAssociadoDetailView.as_view(), name='financeiro_associado'),
    path('dar-baixa-anuidade/<int:pk>/', DarBaixaAnuidadeView.as_view(), name='dar_baixa_anuidade'),
    path('tri-condicoes/', views.associados_triangulo_view, name='tri_condictions'),
    path('descontos-anuidades/', DescontosAnuidadesView.as_view(), name='descontos_anuidades'),
    path('resumo/', ResumoFinanceiroView.as_view(), name='resumo_financeiro'),
    path('despesas/', ListDespesasView.as_view(), name='list_despesas'),
    
    path('associado/<int:associado_id>/aplicar_anuidade/', views.aplicar_anuidade, name='aplicar_anuidade'),
    path('anuidade/desconto/<int:anuidade_associado_id>/', views.conceder_desconto, name='conceder_desconto'),

    path('anuidade/create/', CreateAnuidadeView.as_view(), name='create_anuidade'),
    path('anuidade/edit/<int:pk>/', EditAnuidadeView.as_view(), name='edit_anuidade'),
]