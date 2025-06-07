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
    
    TipoDespesaCreateView,
    DespesaCreateView,
    DespesaUpdateView,

    ListEntradasView,
    EntradaCreateView,
    TipoServicoCreateView,
    EditTipoServicoView,
    EntradaUpdateView,
    RelatorioAnuidadesView,
    )


app_name = 'app_finances'

urlpatterns = [
    path('resumo/', ResumoFinanceiroView.as_view(), name='resumo_financeiro'),
    
    path('anuidades/', views.lista_anuidades, name='list_anuidades'),
    path('financeiro/associado/<int:pk>/', FinanceiroAssociadoDetailView.as_view(), name='financeiro_associado'),
    path('dar-baixa-anuidade/<int:pk>/', DarBaixaAnuidadeView.as_view(), name='dar_baixa_anuidade'),
    path('tri-condicoes/', views.associados_triangulo_view, name='tri_condictions'),
    path('descontos-anuidades/', DescontosAnuidadesView.as_view(), name='descontos_anuidades'),
    path('associado/<int:associado_id>/aplicar_anuidade/', views.aplicar_anuidade, name='aplicar_anuidade'),
    path('anuidade/desconto/<int:anuidade_associado_id>/', views.conceder_desconto, name='conceder_desconto'),
    path('anuidade/create/', CreateAnuidadeView.as_view(), name='create_anuidade'),
    path('anuidade/edit/<int:pk>/', EditAnuidadeView.as_view(), name='edit_anuidade'),
    
    # 🔹 URLs para Tipos de Despesas
    path('despesas/tipos/novo/', TipoDespesaCreateView.as_view(), name='create_tipo_despesa'),
    path('carregar-reparticoes/', views.carregar_reparticoes, name='carregar_reparticoes'),

    # 🔹 URLs para Lançamento de Despesas
    path('despesas/', ListDespesasView.as_view(), name='list_despesas'),
    path('despesas/nova/', DespesaCreateView.as_view(), name='create_despesa'),
    path('despesas/editar/<int:pk>/', DespesaUpdateView.as_view(), name='edit_despesa'),
    #path('despesas/deletar/<int:pk>/', DespesaDeleteView.as_view(), name='delete_despesa'),
    
    # Entradas
    path('entradas/', ListEntradasView.as_view(), name='list_entradas'),  # 📌 Listar Entradas
    path('entradas/nova/', EntradaCreateView.as_view(), name='create_entrada'),  # 📌 Criar Nova Entrada
    path('tipos-servicos/novo/', TipoServicoCreateView.as_view(), name='create_tipo_servico'),
    path('servico/editar/<int:pk>/', EditTipoServicoView.as_view(), name='edit_tipo_servico'),
    path('entradas/editar/<int:pk>/', EntradaUpdateView.as_view(), name='edit_entrada'),
    path('entradas/pagar/<int:entrada_id>/', views.registrar_pagamento, name='registrar_pagamento'),
    
    # Relatórios
    path('relatorio-anuidades/', RelatorioAnuidadesView.as_view(), name='relatorio_anuidades'),
    # Filtra serviços para servir App Serviços
    path('filtrar-tipos-por-natureza/', views.filtrar_tipos_por_natureza, name='filtrar_tipos'),
]