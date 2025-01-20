# Views Manager
from django.urls import path
from .views import (
    DashboardView,
    FinancesAssociacaoView,
    FinancesSuperView,
    AdminDashboardView,
    DelegadoDashboardView,
    AuxiliarAssociacaoDashboardView,
    AuxiliarReparticaoDashboardView,
    DiretorAssociacaoDashboardView,
    PresidenteAssociacaoDashboardView,
    AssociadoDashboardView,
    UserVipDashboardView
    )

app_name = 'app_manager'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='super_dashboard'),
    path('finances-super/', FinancesSuperView.as_view(), name='finances_super'),
    path('finances-associacao/', FinancesAssociacaoView.as_view(), name='finances_associacao'),
    path('admin_dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('delegado_dashboard/', DelegadoDashboardView.as_view(), name='delegado_dashboard'),
    path('auxiliar_associacao_dashboard/', AuxiliarAssociacaoDashboardView.as_view(), name='auxiliar_associacao_dashboard'),
    path('auxiliar_reparticao_dashboard/', AuxiliarReparticaoDashboardView.as_view(), name='auxiliar_reparticao_dashboard'),
    path('diretor_associacao_dashboard/', DiretorAssociacaoDashboardView.as_view(), name='diretor_associacao_dashboard'),
    path('presidente_associacao_dashboard/', PresidenteAssociacaoDashboardView.as_view(), name='presidente_associacao_dashboard'),
    path('associado_dashboard/', AssociadoDashboardView.as_view(), name='associado_dashboard'),

    # Outras URLs...
    path('user_vip/', UserVipDashboardView.as_view(), name='user_vip_dasboard'),
]