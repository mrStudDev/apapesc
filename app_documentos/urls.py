from django.urls import path
from .views import criar_copia_pdf

from .views import (
    DocumentoUploadView,
    TipoDocumentoCreateView,
    TipoDocListView,
    DocumentoDetailView,
    DocumentoDeleteView
    )



app_name = 'app_documentos'

urlpatterns = [
    path('upload/<str:tipo>/<int:id>/', DocumentoUploadView.as_view(), name='upload_documento'),
    path('tipo-documento/create/', TipoDocumentoCreateView.as_view(), name='create_tipo_documento'),
    path('tipo-documento/list/', TipoDocListView.as_view(), name='list_tipo_documento'),

    path('detail/<int:pk>/', DocumentoDetailView.as_view(), name='documento_detail'),  # Detalhes do documento
    path('delete/<int:pk>/', DocumentoDeleteView.as_view(), name='delete_documento'),
    path('criar_pdf/<int:pk>/', criar_copia_pdf, name='criar_copia_pdf'),
]