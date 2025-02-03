from django.urls import path
from app_finances import views
from .views import FinanceiroAssociadoDetailView, DarBaixaAnuidadeView, ResumoFinanceiroView, ListDespesasView


app_name = 'app_finances'

urlpatterns = [
    path('anuidades/', views.lista_anuidades, name='list_anuidades'),
    path('financeiro/associado/<int:pk>/', FinanceiroAssociadoDetailView.as_view(), name='financeiro_associado'),
    path('dar-baixa-anuidade/<int:pk>/', DarBaixaAnuidadeView.as_view(), name='dar_baixa_anuidade'),
    path('resumo/', ResumoFinanceiroView.as_view(), name='resumo_financeiro'),
    path('despesas/', ListDespesasView.as_view(), name='list_despesas'),
]