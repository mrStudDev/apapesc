from django.urls import path
from .views import upload_pdf_base, ListaTodosArquivosView
from . import views


app_name = 'app_automacoes'

urlpatterns = [
    # Uploads
    path('upload/residencia/', upload_pdf_base, {'automacao': 'residencia'}, name='upload_pdf_residencia'),
    path('upload/filiacao/', upload_pdf_base, {'automacao': 'filiacao'}, name='upload_pdf_filiacao'),
    path('upload/atividade-pesqueira/', upload_pdf_base, {'automacao': 'atividade_pesqueira'}, name='upload_pdf_atividade_pesqueira'),
    path('upload/hipossuficiencia/', upload_pdf_base, {'automacao': 'hipossuficiencia'}, name='upload_pdf_hipossuficiencia'),
    path('upload/procuracao-juridica/', upload_pdf_base, {'automacao': 'procuracao_juridica'}, name='upload_pdf_procuracao_juridica'),
    path('lista/todos-arquivos/', ListaTodosArquivosView.as_view(), name='lista_automacoes'),
    
    # Ações
    path('pagina-acoes/', views.pagina_acoes, name='pagina_acoes'),
    path('pagina-acoes/<int:associado_id>/', views.pagina_acoes, name='pagina_acoes'),
    
    # Deletes
    path('delete-pdf/<str:automacao>/<int:declaracao_id>/', views.delete_pdf, name='delete_pdf'),

    # Automações - Gerar
    path('declaracao/filiado/<int:associado_id>/', views.gerar_declaracao_filiado,
         name='gerar_declaracao_filiado'),
        
    path('declaracao/residencia/<int:associado_id>/', views.gerar_declaracao_residencia,
         name='gerar_declaracao_residencia'),    
    
    path('declaracao/atividade/<int:associado_id>/', views.gerar_declaracao_atividade_pesqueira,
         name='gerar_declaracao_atividade_pesqueira'),

    path('declaracao/hipossuficiencia/<int:associado_id>/', views.gerar_declaracao_hipo,
         name='gerar_declaracao_hipo'),

    path('procuracao/juridica/<int:associado_id>/', views.gerar_procuracao_juridica,
         name='gerar_procuracao_juridica'),
]
