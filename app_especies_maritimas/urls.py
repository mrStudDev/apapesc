from django.urls import path
from .views import ListEspecieMarinhaView, SingleEspecieMarinhaView, SingleReceitaView

app_name = 'app_especies_marinhas'

urlpatterns = [
    path('especies/', ListEspecieMarinhaView.as_view(), name='list_especies'),
    path('especies/<slug:slug>/', SingleEspecieMarinhaView.as_view(), name='single_especie'),
    path('receita/<int:pk>/', SingleReceitaView.as_view(), name='single_receita'),
]