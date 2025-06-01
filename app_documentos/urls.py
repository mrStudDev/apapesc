from django.urls import path
from .views import criar_copia_pdf, download_documento, upload_docs_view

from .views import (
    DocumentoUploadView,
    TipoDocumentoCreateView,
    TipoDocListView,
    DocumentoDetailView,
    DocumentoDeleteView,
    TipoDocumentoEditView
    )



app_name = 'app_documentos'

urlpatterns = [
    path('upload/<str:tipo>/<int:id>/', DocumentoUploadView.as_view(), name='upload_documento'),
    path('tipo-documento/create/', TipoDocumentoCreateView.as_view(), name='create_tipo_documento'),
    path('tipo-documento/list/', TipoDocListView.as_view(), name='list_tipo_documento'),
    path('tipo-documento/<int:pk>/editar/', TipoDocumentoEditView.as_view(), name='edit_tipo_documento'),

    path('detail/<int:pk>/', DocumentoDetailView.as_view(), name='documento_detail'),  # Detalhes do documento
    path('delete/<int:pk>/', DocumentoDeleteView.as_view(), name='delete_documento'),
    path('criar_pdf/<int:pk>/', criar_copia_pdf, name='criar_copia_pdf'),
    path('documento/<int:pk>/download/', download_documento, name='download_documento'),
    
    # Upload to Drive Folder
     path('upload/<int:associado_id>/', upload_docs_view, name='upload_docs'),
]    
