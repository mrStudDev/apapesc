# Views Manager
from django.urls import path
from .views import DashboardView, FinancesView

app_name = 'app_manager'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('finances/', FinancesView.as_view(), name='finances'),

    # Outras URLs...
]