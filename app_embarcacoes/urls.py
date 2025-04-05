# app_embarcacoes/urls.py

from django.urls import path


from .views import (
    CreateEmbarcacaoView,
    ListEmbarcacoesView,
    SingleEmbarcacaoView,
    EditEmbarcacaoView
    )

app_name = 'app_embarcacoes'

urlpatterns = [
    path('nova/<int:associado_id>/', CreateEmbarcacaoView.as_view(), name='create_embarcacao'),
    path('lista/', ListEmbarcacoesView.as_view(), name='list_embarcacoes'),
    path('detalhe/<int:pk>/', SingleEmbarcacaoView.as_view(), name='single_embarcacao'),
    path('editar/<int:pk>/', EditEmbarcacaoView.as_view(), name='edit_embarcacao'),
]
