from django.urls import path
from .views import NotaCreateView, NotasListView

app_name = 'app_editor'

urlpatterns = [
    path('', NotasListView.as_view(), name='list_notas'),
    path('create/', NotaCreateView.as_view(), name='create_nota'),
]
