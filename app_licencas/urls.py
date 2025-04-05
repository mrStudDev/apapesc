# app_licencas/urls.py
from django.urls import path

from .views import (
    CreateLicencaView,
    EditLicencaView,
    ListLicencasView,
    SingleLicencaView,
    DeleteLicencaView,
)


app_name = 'app_licencas'

urlpatterns = [
    path('nova/<int:embarcacao_id>/', CreateLicencaView.as_view(), name='create_licenca'),
    path('licenca/<int:pk>/', SingleLicencaView.as_view(), name='single_licenca'),
    path('editar/<int:pk>/', EditLicencaView.as_view(), name='edit_licenca'),
    path('listar/', ListLicencasView.as_view(), name='list_licencas'),
    path('licenca/<int:pk>/deletar/', DeleteLicencaView.as_view(), name='delete_licenca'),
]