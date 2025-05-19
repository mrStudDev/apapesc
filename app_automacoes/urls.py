from django.urls import path
from .views import upload_pdf_base, ListaTodosArquivosView
from . import views

# Gerar declarações e carteirinha list documentos uploads app_automaçoes Templates
app_name = 'app_automacoes'

urlpatterns = [
     # Uploads
     path('upload/residencia/', upload_pdf_base, {'automacao': 'residencia'}, name='upload_pdf_residencia'),
     path('upload/filiacao/', upload_pdf_base, {'automacao': 'filiacao'}, name='upload_pdf_filiacao'),
     path('upload/atividade-pesqueira/', upload_pdf_base, {'automacao': 'atividade_pesqueira'}, name='upload_pdf_atividade_pesqueira'),
     path('upload/hipossuficiencia/', upload_pdf_base, {'automacao': 'hipossuficiencia'}, name='upload_pdf_hipossuficiencia'),
     path('upload/procuracao-juridica/', upload_pdf_base, {'automacao': 'procuracao_juridica'}, name='upload_pdf_procuracao_juridica'),
     path('upload/recibo-anuidade/', upload_pdf_base, {'automacao': 'recibos_anuidades'}, name='upload_pdf_recibo_anuidade'),
     path('upload/cobranca-anuidade/', upload_pdf_base, {'automacao': 'cobranca_anuidades'}, name='upload_pdf_cobranca_anuidade'),
     path('upload/recibo-servico-extra/', upload_pdf_base, {'automacao': 'recibos_servicos_extra'}, name='upload_pdf_recibo_servico_extra'),
     path('upload/carteirinha/', upload_pdf_base, {'automacao': 'carteirinha_apapesc'}, name='upload_pdf_carteirinha_apapesc'),
     path('upload/recibo-anuidade/<int:anuidade_assoc_id>/', upload_pdf_base, {'automacao': 'recibos_anuidades'}, name='upload_pdf_recibo_anuidade'),

     path('lista/todos-arquivos/', ListaTodosArquivosView.as_view(), name='lista_automacoes'),
     
     # Ações
     path('pagina-acoes/', views.pagina_acoes, name='pagina_acoes'),
     path('pagina-acoes/<int:associado_id>/', views.pagina_acoes, name='pagina_acoes'),
     
     path('pagina-acoes-entrada/<int:entrada_id>/', views.pagina_acoes, name='pagina_acoes_entrada'),
     
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
     
     path('gerar-recibo-anuidade/<int:anuidade_assoc_id>/', views.gerar_recibo_anuidade, 
          name='gerar_recibo_anuidade'),

     path('gerar-cobranca-anuidade/<int:anuidade_assoc_id>/', views.gerar_cobranca_anuidade,
          name='gerar_cobranca_anuidade'),     
     
     path('gerar-cobrancas-em-lote/',views.gerar_cobrancas_em_lote, 
          name='gerar_cobrancas_em_lote'),

     
     path('gerar-recibo-servico-extra/<int:entrada_id>/', views.gerar_recibo_entrada_extra, 
          name='gerar_recibo_servico_extra'),
     
     path('gerar-carteirinha/<int:associado_id>/', views.gerar_carteirinha_apapesc,
          name='gerar_carteirinha_apapesc'), 

]
