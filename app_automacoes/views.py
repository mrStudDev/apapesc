from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from accounts.mixins import GroupPermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageBreak
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings
from django.urls import reverse
from urllib.parse import urlencode
from django.contrib.staticfiles import finders
from reportlab.lib.colors import lightgrey, grey
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import Color
from pdfrw.buildxobj import pagexobj

from app_finances.models import AnuidadeAssociado, AnuidadeModel
from app_associados.models import AssociadoModel
from app_associacao.models import AssociacaoModel
from django.contrib import messages
from app_finances.models import EntradaFinanceira

from slugify import slugify

from .models import (
    DeclaracaoResidenciaModel,
    DeclaracaoFiliacaoModel,
    DeclaracaoAtividadePesqueiraModel,
    DeclaracaoHipossuficienciaModel,
    ProcuracaoJuridicaModel,
    ReciboAnuidadeModel,
    ReciboServicoExtraModel,
    CarteirinhaAssociadoModel,
    CobrancaAnuidadeModel,
    ProcuracaoAdministrativaModel,
    AutorizacaoDireitoImagemModel,
    AutorizacaoAcessoGovModel,
    DeclaracaoDesfiliacaoModel,
    DireitosDeveres,
    RetiradaDocumentos,
    )

# Deletes
# Mapeamento de automações para modelos
MODELO_MAP = {
    'residencia': DeclaracaoResidenciaModel,
    'filiacao': DeclaracaoFiliacaoModel,
    'atividade_pesqueira': DeclaracaoAtividadePesqueiraModel,
    'hipossuficiencia': DeclaracaoHipossuficienciaModel,
    'procuracao_juridica': ProcuracaoJuridicaModel,
    'recibos_anuidades': ReciboAnuidadeModel,
    'recibos_servicos_extra': ReciboServicoExtraModel,
    'carteirinha_apapesc': CarteirinhaAssociadoModel,
    'cobranca_anuidades': CobrancaAnuidadeModel,
    'procuracao_administrativa': ProcuracaoAdministrativaModel,
    'autorizacao_direito_imagem': AutorizacaoDireitoImagemModel,
    'autorizacao_acesso_gov': AutorizacaoAcessoGovModel,
    'declaracao_desfiliacao': DeclaracaoDesfiliacaoModel,
    'direitos_deveres':DireitosDeveres,
    'retirada_documentos': RetiradaDocumentos,

}

def delete_pdf(request, automacao, declaracao_id):
    if request.method == "POST":
        # Obter o modelo correspondente pelo tipo de automação
        modelo = MODELO_MAP.get(automacao)
        if not modelo:
            messages.error(request, "Tipo de automação inválido.")
            return redirect('app_automacoes:lista_automacoes')

        # Obter a declaração pelo ID
        declaracao = get_object_or_404(modelo, id=declaracao_id)
        
        # Excluir o arquivo do sistema de arquivos
        if declaracao.pdf_base:
            declaracao.pdf_base.delete()  # Remove o arquivo do sistema

        # Excluir o registro do banco de dados
        declaracao.delete()
        messages.success(request, f"{automacao.replace('_', ' ').capitalize()} excluído(a) com sucesso!")

    return redirect('app_automacoes:lista_automacoes')



# UPLOAD DE MODELOS PDF BASE
def upload_pdf_base(request, automacao):
    modelo_map = {
        'residencia': DeclaracaoResidenciaModel,
        'filiacao': DeclaracaoFiliacaoModel,
        'atividade_pesqueira': DeclaracaoAtividadePesqueiraModel,
        'hipossuficiencia': DeclaracaoHipossuficienciaModel,
        'procuracao_juridica': ProcuracaoJuridicaModel,
        'recibos_anuidades': ReciboAnuidadeModel,
        'recibos_servicos_extra': ReciboServicoExtraModel,
        'carteirinha_apapesc': CarteirinhaAssociadoModel,
        'cobranca_anuidades': CobrancaAnuidadeModel,
        'procuracao_administrativa': ProcuracaoAdministrativaModel,
        'autorizacao_direito_imagem': AutorizacaoDireitoImagemModel,
        'autorizacao_acesso_gov': AutorizacaoAcessoGovModel,
        'declaracao_desfiliacao': DeclaracaoDesfiliacaoModel,
        'direitos_deveres':DireitosDeveres,
        'retirada_documentos': RetiradaDocumentos,
    }
    
    modelo = modelo_map.get(automacao)
    if not modelo:
        return HttpResponse("Automação inválida.", status=400)

    if request.method == "POST":
        pdf_base = request.FILES.get('pdf_base')
        if not pdf_base:
            return HttpResponse("Arquivo PDF não enviado.", status=400)

        # Tenta pegar a primeira instância existente; se não houver, cria nova
        instancia = modelo.objects.first()
        if not instancia:
            instancia = modelo()

        # Atribui o novo arquivo e salva
        instancia.pdf_base = pdf_base
        instancia.save()

        return redirect('app_automacoes:lista_automacoes')  # Ajuste conforme sua url de destino

    # Para requisições GET, exibe o template com formulário de upload
    return render(request, 'app_automacoes/upload_pdf_base.html', {'automacao': automacao})




class ListaTodosArquivosView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_automacoes/list_automacoes.html'
    group_required = ['Superuser','Admin da Associação']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicione cada queryset com nome separado
        context['declaracoes_residencia'] = DeclaracaoResidenciaModel.objects.all()
        context['declaracoes_filiacao'] = DeclaracaoFiliacaoModel.objects.all()
        context['declaracoes_atividade_pesqueira'] = DeclaracaoAtividadePesqueiraModel.objects.all()
        context['declaracoes_hipossuficiencia'] = DeclaracaoHipossuficienciaModel.objects.all()
        context['procuracoes_procuracao_juridica'] = ProcuracaoJuridicaModel.objects.all()
        context['recibos_anuidades'] = ReciboAnuidadeModel.objects.all()
        context['recibos_servicos_extra'] = ReciboServicoExtraModel.objects.all()
        context['carteirinha_apapesc'] = CarteirinhaAssociadoModel.objects.all()
        context['cobranca_anuidades'] = CobrancaAnuidadeModel.objects.all()
        context['procuracoes_procuracao_administrativa'] = ProcuracaoAdministrativaModel.objects.all()
        context['autorizacao_direito_imagem'] = AutorizacaoDireitoImagemModel.objects.all()
        context['autorizacao_acesso_gov'] = AutorizacaoAcessoGovModel.objects.all()
        context['declaracao_desfiliacao'] = DeclaracaoDesfiliacaoModel.objects.all()
        context['direitos_deveres'] = DireitosDeveres.objects.all()
        context['retirada_documentos'] = RetiradaDocumentos.objects.all()
        
        return context


# Automações

# PÁGINA DE AÇÕES -  AS AÇÕES GERAR ESTÃO VÍNCULADAS NESSA PÁGINA
def pagina_acoes(request, associado_id=None, entrada_id=None):
    pdf_url = request.GET.get('pdf_url')
    tipo_recibo = request.GET.get('tipo', 'documento')  # 👉 valor padrão agora é "documento"

    associado = None
    entrada = None
    extra_associado = None

    if associado_id:
        associado = get_object_or_404(AssociadoModel, pk=associado_id)

    if entrada_id:
        entrada = get_object_or_404(EntradaFinanceira, pk=entrada_id)
        if hasattr(entrada, 'entrada_servico_extra'):
            extra_associado = entrada.entrada_servico_extra.extra_associado

    associacao = AssociacaoModel.objects.first()
    if not associacao:
        return HttpResponse("Informações da APAPESC não estão configuradas.", status=404)

    return render(request, 'app_automacoes/pagina_acoes.html', {
        'pdf_url': pdf_url,
        'tipo_recibo': tipo_recibo,
        'associado': associado,
        'entrada': entrada,
        'extra_associado': extra_associado,
        'associacao': associacao,
    })

    
#=======================================================================================================

# GERAR DECLARAÇÃO DE FILIADO
def gerar_declaracao_filiado(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)
    associacao = associado.associacao

    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/declaracao_filiacao.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Declaração de Filiação não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)
    template_page = template_pdf.pages[0]  # Primeira página como template

    # Buffer para gerar o PDF dinamicamente
    buffer = BytesIO()

    # Estilos personalizados
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
            parent=styles['Title'],
            fontName='Times-Bold',
            fontSize=11,
            alignment=2,
            leading=32,  # Define a altura da linha
            spaceBefore=100,  # Espaçamento antes do parágrafo
            textColor=lightgrey,
    )

    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=22,  # Espaçamento entre as linhas
        alignment=4
    )

    style_veracidade = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,  # Espaçamento entre as linhas
        alignment=4,
        leftIndent=50,  # Indenta o texto para a direita
    )

    style_data = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,  # Espaçamento entre as linhas
        spaceBefore=10,
        alignment=4
    )

    style_assinatura = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,  # Espaçamento entre as linhas
        alignment=4
    )
    style_presidente = ParagraphStyle(
        'Title',
            parent=styles['Title'],
            fontName='Times-Bold',
            fontSize=12,
            alignment=2,
            leading=32,  # Define a altura da linha
            spaceBefore=100,  # Espaçamento antes do parágrafo
            textColor=grey,
    )
    nome_presidente = ( f"{associacao.presidente.user.get_full_name()}")

    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Texto da declaração
    texto = (
        f"A {associacao.nome_fantasia}, {associacao.razao_social}, "
        f"inscrita no CNPJ sob o nº {associacao.cnpj}, com sede à {associacao.logradouro}, n° {associacao.numero}, "
        f"{associacao.complemento}, {associacao.bairro}, {associacao.municipio} - {associacao.uf}, CEP: {associacao.cep}, "
        f"declara para os devidos fins que <strong>{associado.user.get_full_name()},</strong> inscrito no CPF sob o nº {associado.cpf}, "
        f"e no RG nº {associado.rg_numero} - {associado.rg_orgao}, é filiado(a) a esta entidade desde, "
        f"{associado.data_filiacao.strftime('%d/%m/%Y')}."
    )

    local_data = f"{associacao.municipio}, {data_atual}."

    assinatura = (
        '_________________________________________________________________________<br/>'
        f"{associacao.administrador.user.get_full_name().upper()}<br/>"
        f"PROCURADOR(A) {associacao.nome_fantasia}<br/>"
        f"{associacao.razao_social}"
        f"<br/>Presidente: {associacao.presidente.user.get_full_name().upper()}"
    )

    declaracao_veracidade = (
        "<strong>Declaro sob as penas de lei (Art. 299 do Código Penal) a veracidade das informações "
        "aqui prestadas para emissão desta declaração, ficando sob minha responsabilidade as "
        "informações nelas contidas e eventuais informações não declaradas.</strong>"
    )

    # Criação do Frame para controlar margens e posicionamento
    pdf_canvas = Frame(x1=75, y1=75, width=450, height=700, showBoundary=1)

    # Adiciona o título, texto, local e assinatura ao Frame
    elements = [
        Paragraph(nome_presidente, style_presidente),
        Spacer(1, 90),
                
        Paragraph(texto, style_normal),
        Spacer(1, 14),

        Paragraph(declaracao_veracidade, style_veracidade),
        Spacer(1, 18),

        Paragraph(local_data, style_data),
        Spacer(1, 24),

        Paragraph(assinatura, style_assinatura),
        Spacer(1, 16),

    ]

    # Gerando o conteúdo dinâmico
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=68, leftMargin=68, topMargin=172, bottomMargin=50)
    doc.build(elements)

    # Mesclando o conteúdo dinâmico com o template
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)
    overlay_page = overlay_pdf.pages[0]

    merger = PageMerge(template_page)
    merger.add(overlay_page).render()

    # Salvando o PDF mesclado no sistema de arquivos
    pdf_name = f"declaracao_filiado_{associado_id}_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Redirecionando para a página de ações com o URL do PDF
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    query_string = urlencode({'pdf_url': pdf_url})
    redirect_url = f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?{query_string}"
    return redirect(redirect_url)
#=======================================================================================================


# GERAR DECLARAÇÃO DE ATIVIDADE PESQUEIRA
def gerar_declaracao_atividade_pesqueira(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)
    associacao = associado.associacao
    
    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/declaracao_atividade_pesqueira.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Declaração de Atv. Pesqueira não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)
    template_page = template_pdf.pages[0]  # Primeira página como template

    # Buffer para gerar o PDF dinamicamente
    buffer = BytesIO()

    # Estilos personalizados
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=11,
        alignment=2,
        leading=32,  # Espaçamento entre as linhas do título
        spaceBefore=100,  # Espaçamento antes do título
        textColor=colors.grey,
    )

    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=15,  # Espaçamento entre as linhas do texto
        alignment=4,  # Justificado
    )
    style_presidente = ParagraphStyle(
        'Title',
            parent=styles['Title'],
            fontName='Times-Bold',
            fontSize=12,
            alignment=2,
            leading=32,  # Define a altura da linha
            spaceBefore=100,  # Espaçamento antes do parágrafo
            textColor=grey,
    )
    nome_presidente = ( f"{associacao.presidente.user.get_full_name()}")
    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Texto inicial da declaração
    texto = (
        f"A {associacao.razao_social}, "
        f"inscrita no CNPJ sob n° {associacao.cnpj}, com sede na {associacao.logradouro}, n° {associacao.numero}, "
        f"{associacao.complemento}, {associacao.bairro}, {associacao.municipio} - {associacao.uf}, CEP: {associacao.cep}, "
        f"representada neste ato por seu presidente, {associacao.presidente.user.get_full_name()}, "
        f"{associacao.presidente.profissao}, {associacao.presidente.estado_civil}, portador " 
        f"da carteira de identidade n° {associacao.presidente.rg_numero} - {associacao.presidente.rg_orgao}, inscrito no CPF " 
        f"sob n° {associacao.presidente.cpf}, Residente e domiciliado à {associacao.presidente.logradouro}, " 
        f"n° {associacao.presidente.numero}, {associacao.presidente.complemento}, {associacao.presidente.bairro}, " 
        f"{associacao.presidente.municipio}, {associacao.presidente.uf}, CEP {associacao.presidente.cep}, " 
        f"declara que o Sr(a). <strong>{associado.user.get_full_name()},</strong> "
        f"inscrito no CPF sob o nº <strong>{associado.cpf}</strong>, é pescador registrado no Ministério da Agricultura, "
        f"Pesca e Abastecimento (MAPA), sob o nº <strong>{associado.rgp}</strong>, é residente e domiciliado(a) na {associado.logradouro}, "
        f"nº {associado.numero}, {associado.complemento}, {associado.bairro}, {associado.municipio}, {associado.uf}, CEP: {associado.cep}, "
        f"dedica-se à pesca artesanal profissional, com meios de produção próprios ou em regime de parceria com outros "
        f"pescadores artesanais e que sua renda depende de sua produção."
    )

    local_data = f"FLORIANÓPOLIS, {data_atual}."

    # Dados para a tabela
    dados_tabela = [
        ["ESPÉCIE", "QUANTIDADE MÉDIA ANUAL (Kg)"],  # Cabeçalho da tabela
        [associado.especie1, associado.quantidade1],
        [associado.especie2, associado.quantidade2],
        [associado.especie3, associado.quantidade3],
        [associado.especie4, associado.quantidade4],
        [associado.especie5, associado.quantidade5],
    ]

    # Criação da tabela
    tabela = Table(dados_tabela, colWidths=[200, 200])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    assinatura = (
        "Por ser verdade, firmo e dou Fé.<br/><br/>"
        "__________________________________________________________________________<br/>"
        f"Jurídico {associacao.administrador.user.get_full_name()} | {associacao.administrador.oab} <br/>"        
        f"Presidente da Associação: {associacao.presidente.user.get_full_name()}"

    )

    # Elementos para o PDF
    elements = [
        Paragraph(nome_presidente, style_presidente),
        Spacer(1, 100),
        Paragraph(texto, style_normal),
        Spacer(1, 17),
        tabela,  # Adicionando a tabela ao PDF
        Spacer(1, 15),
        Paragraph(local_data, style_normal),
        Spacer(1, 10),
        Paragraph(assinatura, style_normal),
    ]

    # Gerando o conteúdo dinâmico
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=172, bottomMargin=50)
    doc.build(elements)

    # Mesclando o conteúdo dinâmico com o template
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)
    overlay_page = overlay_pdf.pages[0]

    merger = PageMerge(template_page)
    merger.add(overlay_page).render()

    # Salvando o PDF no disco
    pdf_name = f"declaracao_atividade_pesqueira_{associado_id}_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Redirecionando para a página de ações
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    query_string = urlencode({'pdf_url': pdf_url})
    redirect_url = f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?{query_string}"
    return redirect(redirect_url)


#=======================================================================================================


# GERAR DECLARAÇÃO DE RESIDÊNCIA
def gerar_declaracao_residencia(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)
    associacao = associado.associacao
        
    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/declaracao_residencia.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Declaração de Residência não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)
    template_page = template_pdf.pages[0]  # Primeira página como template

    # Buffer em memória para o conteúdo dinâmico
    buffer = BytesIO()

    # Definindo estilos personalizados
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=16,
        alignment=1,  # Centralizado
        leading=32,  # Espaçamento entre as linhas do título
        spaceBefore=100,  # Espaçamento antes do título
        textColor=colors.grey,
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=28,  # Espaçamento entre linhas
        alignment=4,  # Justificado
    )
    style_assinatura = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=28,  # Espaçamento entre linhas
        alignment=1,  # Centralizado
    )
    style_data = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=28,  # Espaçamento entre linhas
        alignment=0,  # Esquerda
        spaceBefore=20,  # Espaçamento antes do título
    )
    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Texto da declaração
    texto = (
        f"Eu, <strong>{associado.user.get_full_name()}</strong>, inscrito no CPF nº {associado.cpf}, na falta de documentos "
        f"para comprovação de residência, em conformidade com o disposto na Lei 7.115, de 29 de "
        f"agosto de 1983, DECLARO para os devidos fins, sob penas da Lei, que RESIDO no endereço: "
        f"<strong>{associado.logradouro}, nº {associado.numero}, {associado.complemento},"
        f" {associado.bairro}, {associado.municipio} - {associado.uf}, CEP: {associado.cep}.</strong>"
    )

    # Declaração de veracidade
    declaracao_veracidade = (
        "Declaro sob as penas da lei (Art. 299 do Código Penal) a veracidade das informações "
        "aqui prestadas para emissão desta declaração, ficando sob minha responsabilidade as "
        "informações nelas contidas e eventuais informações não declaradas."
    )

    # Local e data
    local_data = f"FLORIANÓPOLIS, {data_atual}."

    # Assinatura
    assinatura = (
        "____________________________________________________________________<br/>"
        f"{associado.user.get_full_name()}  - CPF: {associado.cpf}<br/>"
    )

    # Elementos do PDF na ordem correta
    elements = [
        Paragraph("DECLARAÇÃO DE RESIDÊNCIA", style_title),
        Spacer(1, 20),
        Paragraph(texto, style_normal),
        Spacer(1, 10),
        Paragraph(declaracao_veracidade, style_normal),
        Paragraph(local_data, style_data),
        Spacer(1, 24),
        Paragraph(assinatura, style_assinatura),
        Spacer(1, 26),
    ]

    # Criação do documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=85,
        leftMargin=85,
        topMargin=160,
        bottomMargin=40,
    )

    # Gerar o conteúdo do PDF
    doc.build(elements)

    # Mesclar o conteúdo dinâmico com o template PDF
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)
    overlay_page = overlay_pdf.pages[0]

    merger = PageMerge(template_page)
    merger.add(overlay_page).render()

    # Salvar o PDF em disco
    pdf_name = f"declaracao_residencia_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Construir o URL para o PDF
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"

    # Redirecionar para a página de ações
    query_string = urlencode({'pdf_url': pdf_url})
    redirect_url = f"{reverse('app_automacoes:pagina_acoes', kwargs={'associado_id': associado.id})}?{query_string}"
    return redirect(redirect_url)
# =======================================================================================================


# DECLARAÇÃO DE HIPOSSUFICIÊNCIA
def gerar_declaracao_hipo(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)
    associacao = associado.associacao
    
    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/declaracao_hipossuficiencia.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Declaração de Atv. Pesqueira não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)
    template_page = template_pdf.pages[0]  # Primeira página como template

    # Buffer em memória para o conteúdo dinâmico
    buffer = BytesIO()

    # Definindo estilos personalizados
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=16,
        alignment=1,  # Centralizado
        leading=32,  # Espaçamento entre as linhas do título
        spaceBefore=100,  # Espaçamento antes do título
        textColor=colors.grey,
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=22,  # Espaçamento entre linhas
        alignment=4,  # Justificado
    )
    style_assinatura = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=28,  # Espaçamento entre linhas
        alignment=1,  # Centralizado
    )
    style_data = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=28,  # Espaçamento entre linhas
        alignment=0,  # Esquerda
        spaceBefore=50,  # Espaçamento antes do título
    )
    style_veracidade = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,  # Espaçamento entre as linhas
        alignment=4,
        leftIndent=50,  # Indenta o texto para a direita
    )

    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Texto da declaração
    texto = (
        f"Eu, <strong>{associado.user.get_full_name()}</strong>, profissão {associado.profissao}, "
        f"estado civil {associado.estado_civil}, inscrito(a) no CPF nº {associado.cpf}, e RG: nº{associado.rg_numero}, "
        f"com domicílio e residência estabelecido à {associado.logradouro}, nº {associado.numero}, {associado.complemento}, {associado.bairro}, "
        f"{associado.municipio} - {associado.uf} {associado.cep}. <strong>DECLARO</strong>, para todos os fins de "
        f"direito e sob as penas da lei, que não tenho condições de arcar com as despesas inerentes ao presente "
        f"processo, sem prejuízo do meu sustento e de minha família, necessitando, portanto, da "
        f"<strong>GRATUIDADE DA JUSTIÇA</strong>, nos termos do art. 98 e seguintes da Lei 13.105/2015 "
        f"(Código de Processo Civil). Requeiro, ainda, que o benefício abarque todos os atos do processo."
    )

    # Declaração de veracidade
    declaracao_veracidade = (
        "<strong>Declaro sob as penas da lei (Art. 299 do Código Penal) a veracidade das informações "
        "aqui prestadas para emissão desta declaração, ficando sob minha responsabilidade as "
        "informações nelas contidas e eventuais informações não declaradas.</strong>"
    )

    # Local e data
    local_data = f"{associado.reparticao.municipio_sede}, {data_atual}."

    # Assinatura
    assinatura = (
        "____________________________________________________________________<br/>"
        f"{associado.user.get_full_name()} - CPF: {associado.cpf}<br/>"
    )

    # Elementos do PDF na ordem correta
    elements = [
        Paragraph("DECLARAÇÃO DE HIPOSSUFICIÊNCIA", style_title),
        Spacer(1, 20),
        Paragraph(texto, style_normal),
        Spacer(1, 10),
        Paragraph(declaracao_veracidade, style_veracidade),
        Paragraph(local_data, style_data),
        Spacer(1, 14),
        Paragraph(assinatura, style_assinatura),
        Spacer(1, 26),
    ]

    # Criação do documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=85,
        leftMargin=85,
        topMargin=160,
        bottomMargin=40
    )

    # Gerar o conteúdo do PDF
    doc.build(elements)

    # Mesclar o conteúdo dinâmico com o template PDF
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)
    overlay_page = overlay_pdf.pages[0]

    merger = PageMerge(template_page)
    merger.add(overlay_page).render()

    # Salvar o PDF no disco
    pdf_name = f"declaracao_hipo_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Construir o URL do PDF
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"

    # Redirecionar para a página de ações com o URL do PDF
    query_string = urlencode({'pdf_url': pdf_url})
    redirect_url = f"{reverse('app_automacoes:pagina_acoes', kwargs={'associado_id': associado.id})}?{query_string}"
    return redirect(redirect_url)


# GERAR PROCURAÇÃO AD JUDICIA
def gerar_procuracao_juridica(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)

    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/procuracao_juridica.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Procuração Jurídica não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)

    # Buffer em memória para o conteúdo dinâmico
    buffer = BytesIO()

    # Definindo estilos personalizados
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=17,
        alignment=1,  # Centralizado
        leading=32,  # Espaçamento entre as linhas do título
        spaceBefore=100,  # Espaçamento antes do título
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=4,  # Justificado
    )
    style_assinatura = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=1,  # Justificado
    )
    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Texto da declaração
    texto1 = (
        f"<strong>OUTORGANTE(S)</strong>: <strong>{associado.user.get_full_name()}</strong>, brasileira, "
        f"profissão, {associado.profissao}, estado civil, {associado.estado_civil}, CPF nº {associado.cpf}, "
        f"RG nº {associado.rg_numero}, com residência e domicílio estabelecido á {associado.logradouro}, "
        f"nº {associado.numero}, {associado.complemento}, {associado.bairro}, {associado.municipio} -"
        f" {associado.uf} {associado.cep}. "
        f"<br /><br /><strong>OUTORGADOS</strong>: <strong>CRISTIANI JORDANI DOS SANTOS RAMOS</strong>, "
        f"brasileira, casada, advogada, inscrição na OAB/SC sob o número 51.410, inscrita no CPF 853.801.219-34, "
        f"<strong>SAMARA IZILDA CORREA DOS SANTOS</strong>,  brasileira, divorciada,"
        f"advogada, inscrição na OAB/SC sob o número 51.380, inscrita no CPF 027.034.419-59, integrantes do "
        f"escritório JORDANI & SANTOS Advogados Associados."
    )
    texto2 =(
        f"<strong>PODERES:</strong> Nos termos do art. 105 do CPC para o foro em geral, conferindo-lhe os mais amplos"
        f" e ilimitados poderes inclusive os da cláusula “ad judicia et extra”, para, onde com esta se apresentar, "
        f"em conjunto ou separadamente, independente de ordem de nomeação, propor ações e contestá-las, receber "
        f"citações, notificações e intimações, apresentar justificações, variar de ações e pedidos, notificar, "
        f"interpelar, protestar, discordar, transigir e desistir, receber a quantia e dar quitação, arrematar "
        f"ou adjudicar em qualquer praça ou leilão, reter dos valores finais auferidos na demanda,  honorários "
        f"contratuais de 30% e também o valor equivalente a três benefícios estabelecidos em sentença, prestar "
        f"compromissos de inventariante, oferecer as primeiras e últimas declarações, interpor quaisquer recursos, "
        f"requerer, assinar, praticar, perante qualquer repartição pública, entidades autárquicas e ou parestatal, "
        f"Juízo, Instância ou Tribunal, tudo o que julgar conveniente ou necessário ao bom e fiel desempenho deste "
        f"mandato, que poderá ser substabelecido, no todo ou em parte, a quem melhor lhe convier, com ou sem reserva "
        f"de poderes, EM ESPECIAL PARA PROPOR AÇÃO JUDICIAL DE APOSENTADORIA BEM COMO, POR FORÇA DO ARTIGO 661 DO "
        f"Código Civil, PRESTAR OU ASSINAR DECLARAÇÃO DE ISENÇÃO DO IMPOSTO DE RENDA."
    )

    # Local e data
    local_data = f"{associado.reparticao.municipio_sede}, {data_atual}."
    assinatura = (
        "____________________________________________________________________<br/>"
        f"<strong>{associado.user.get_full_name()}</strong><br/>"
        f"CPF: {associado.cpf}<br/>"
    )

    # Elementos do PDF
    elements = [
        Paragraph("PROCURAÇÃO AD JUDICIA", style_title),
        Spacer(1, 10),
        Paragraph(texto1, style_normal),
        Spacer(1, 10),
        Paragraph(texto2, style_normal),
        Spacer(1, 10),
        Paragraph(local_data, style_normal),
        Spacer(1, 24),
        Paragraph(assinatura, style_assinatura),
    ]

    # Criando o documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=85,
        leftMargin=85,
        topMargin=140,
        bottomMargin=40,
    )

    doc.build(elements)

    # Mesclando o conteúdo dinâmico com o template
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)

    # **Ajuste Importante:**
    # O número de páginas do template e o overlay_pdf deve ser gerenciado com cuidado.
    for index, template_page in enumerate(template_pdf.pages):
        if index < len(overlay_pdf.pages):
            overlay_page = overlay_pdf.pages[index]
            PageMerge(template_page).add(overlay_page).render()

    # Salvando o PDF final
    pdf_name = f"procuracao_juridica_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Preparando o redirecionamento
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?pdf_url={pdf_url}")
# ======================================================================================================

# GERAR RECIBO DE ANUIDADE
from decimal import Decimal
from django.db.models import Sum

def gerar_recibo_anuidade(request, anuidade_assoc_id):
    anuidade_assoc = get_object_or_404(AnuidadeAssociado, id=anuidade_assoc_id)
    associado = anuidade_assoc.associado
    associacao = associado.associacao

    # ⚠️ Verifica se existe pagamento ou desconto suficiente
    total_pago = anuidade_assoc.pagamentos.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    total_desconto = anuidade_assoc.descontos.aggregate(total=Sum('valor_desconto'))['total'] or Decimal('0.00')
    valor_anuidade = anuidade_assoc.anuidade.valor_anuidade
    soma_total = total_pago + total_desconto

    if soma_total < valor_anuidade:
        return HttpResponse("Ainda há saldo devedor. O recibo será gerado apenas quando o total for quitado (via pagamento ou desconto).", status=400)

    # ⚠️ Verifica se o template existe
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/recibo_anuidade.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para o Recibo de Anuidade não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)

    # Dados de pagamento
    ultimo_pagamento = anuidade_assoc.pagamentos.order_by('-data_pagamento').first()
    data_pagamento = (
        ultimo_pagamento.data_pagamento.strftime('%d/%m/%Y')
        if ultimo_pagamento else datetime.now().strftime('%d/%m/%Y')
    )
    data_hoje = datetime.now().strftime('%d/%m/%Y')

    # Construção do texto dinâmico
    texto = (
        f"Recebemos de <strong>{associado.user.get_full_name()}</strong>, "
        f"inscrito no CPF sob o nº <strong>{associado.cpf}</strong>, "
        f"a importância de <strong>R$ {total_pago:.2f}</strong> referente ao pagamento da anuidade do exercício de <strong>{anuidade_assoc.anuidade.ano}</strong>."
    )

    if total_desconto > 0:
        texto += f" Um desconto de <strong>R$ {total_desconto:.2f}</strong> foi concedido, totalizando o valor integral de <strong>R$ {valor_anuidade:.2f}</strong>."

    texto += (
        f"<br/><br/>Este pagamento foi efetuado à <strong>{associacao.razao_social}</strong>, "
        f"inscrita no CNPJ sob o nº {associacao.cnpj}, com sede na {associacao.logradouro}, nº {associacao.numero}, "
        f"{associacao.bairro}, {associacao.municipio or 'Município não informado'}/{associacao.uf}. "
        f"<br/><br/><i>Agradecemos por sua confiança. A contribuição anual é essencial para a manutenção das atividades da associação, refletindo diretamente no apoio prestado à categoria.</i>"
    )

    assinatura = (
        f"{associacao.presidente.user.get_full_name()}<br/>"
        f"Presidente da Associação<br/>"
        f"Forte abraço!"
    )

    municipio = associacao.municipio.upper() if associacao.municipio else "CIDADE NÃO DEFINIDA"
    local_data = f"{municipio}, {data_hoje}."

    # PDF Elements
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=14, alignment=TA_CENTER, leading=28, spaceBefore=40)
    style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=18, alignment=TA_JUSTIFY)
    style_assinatura = ParagraphStyle('Assinatura', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, leading=18, alignment=TA_CENTER)
    style_presidente = ParagraphStyle('Presidente', parent=styles['Normal'], fontName='Times-Bold', fontSize=12, alignment=2, textColor=colors.grey)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=120, bottomMargin=50)
    elements = [
        Spacer(1, 50),
        Paragraph(associacao.presidente.user.get_full_name(), style_presidente),
        Spacer(1, 35),
        Paragraph("RECIBO DE PAGAMENTO DE ANUIDADE", style_title),
        Spacer(1, 20),
        Paragraph(texto, style_normal),
        Spacer(1, 24),
        Paragraph(local_data, style_normal),
        Spacer(1, 20),
        Paragraph(assinatura, style_assinatura),
    ]
    doc.build(elements)
    buffer.seek(0)

    overlay_pdf = PdfReader(buffer)
    for index, template_page in enumerate(template_pdf.pages):
        if index < len(overlay_pdf.pages):
            overlay_page = overlay_pdf.pages[index]
            PageMerge(template_page).add(overlay_page).render()

    # Geração do arquivo
    nome_associado = slugify(associado.user.get_full_name())
    pdf_name = f"recibo_anuidade_{associado.id}_{nome_associado}_{anuidade_assoc.anuidade.ano}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Redireciona com o link do PDF
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    query_string = urlencode({'pdf_url': pdf_url})
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?{query_string}&tipo=anuidade")

    # =======================================================================================================
# GERAR COBRANÇA NUIDADE APAPESC ASSOCIADO
# app_automacoes/views.py
from decimal import Decimal

def gerar_cobranca_anuidade(request, anuidade_assoc_id):
    anuidade_assoc = get_object_or_404(AnuidadeAssociado, id=anuidade_assoc_id)
    associado = anuidade_assoc.associado
    associacao = associado.associacao

    # Caminho para o PDF base
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/cobranca_anuidades.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Cobrança de Anuidade não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)
    buffer = BytesIO()

    hoje = datetime.now()
    data_hoje = hoje.strftime('%d/%m/%Y')

    # 🔎 Pega todas as anuidades não pagas de anos anteriores ao atual
    anuidades_em_aberto = AnuidadeAssociado.objects.filter(
        associado=associado,
        pago=False,
        anuidade__ano__lt=hoje.year
    ).select_related('anuidade')

    if not anuidades_em_aberto.exists():
        return HttpResponse("Não há anuidades em aberto para este associado.", status=404)

    # 🔢 Conta de quantas anuidades estão em aberto
    total_anuidades_em_aberto = anuidades_em_aberto.count()

    # 💰 Valor atual da anuidade (do ano corrente)
    try:
        anuidade_atual = AnuidadeModel.objects.get(ano=hoje.year)
    except AnuidadeModel.DoesNotExist:
        return HttpResponse("Valor da anuidade atual não encontrado.", status=404)

    valor_anuidade_atual = anuidade_atual.valor_anuidade
    valor_total_cobrado = valor_anuidade_atual * total_anuidades_em_aberto

    # 🧾 Lista das anuidades em aberto com seus valores originais
    lista_anuidades = " - ".join([
        f"<strong>{a.anuidade.ano}</strong>: R$ {a.anuidade.valor_anuidade:.2f}"
        for a in anuidades_em_aberto
    ])


    # 📝 Texto da carta
    texto = f"""
    <br/><br/>
    Prezado(a) <strong>{associado.user.get_full_name()}</strong>,<br/><br/>

    Realizamos uma análise em nosso sistema e identificamos que, até o momento, não localizamos o seu nome nas listagens de pagamentos das seguintes anuidades:

    {lista_anuidades}. Também não identificamos o envio de comprovantes de pagamento para os anos mencionados. Se os pagamentos já foram realizados, por gentileza, envie os comprovantes para que possamos atualizar sua situação.<br/><br/>

    Caso ainda não tenha efetuado os pagamentos, o valor a ser considerado é com base na anuidade vigente(atual) ({hoje.year}), que é no valor de <strong>R$ {valor_anuidade_atual:.2f}</strong> por ano em aberto.

    Sendo assim, o valor total das anuidade(es) em aberto é de: <strong>R$ {valor_total_cobrado:.2f}</strong>.<br/><br/>
    
    <strong>OBS:</strong> As anuidades computadas nesse documento são de anos <font color='red'><strong>anteriores</strong></font> ao ano vigente (atual).<br/><br/>

    Entre em contato para verificar as formas de pagamento. <strong>Facilitamos para voçê!</strong> <br/><br/>

    <em>Agradecemos por sua atenção. A sua contribuição fortalece a associação e nos permite seguir prestando apoio e serviços aos associados.</em>
    """

    assinatura = (
        f"{associacao.presidente.user.get_full_name()}<br/>"
        f"Presidente da Associação<br/>"
        f"APAPESC"
    )

    municipio = associacao.municipio.upper() if associacao.municipio else "CIDADE NÃO DEFINIDA"
    local_data = f"{municipio}, {data_hoje}."

    # Estilos PDF
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=14,
        alignment=TA_CENTER,
        leading=20,
        spaceBefore=27,
        textColor=colors.black,
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=17,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
    )
    style_assinatura = ParagraphStyle(
        'Assinatura',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,
        alignment=TA_CENTER,
        spaceBefore=10,
    )
    style_presidente = ParagraphStyle(
        'Presidente',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        alignment=2,
        leading=16,
        spaceBefore=10,  # 🔼 Menos espaço acima
        textColor=colors.grey,
    )
    nome_presidente = ( f"{associacao.presidente.user.get_full_name()}")
    # Gera conteúdo do PDF
    elements = [
        Spacer(1, 61),
        Paragraph(nome_presidente, style_presidente),
        Spacer(1, 35),
        Paragraph("ANUIDADES EM ABERTO", style_title),
        Spacer(1, 1),
        Paragraph(texto, style_normal),
        Spacer(1, 7),
        Paragraph(local_data, style_normal),
        Spacer(1, 7),
        Paragraph(assinatura, style_assinatura),
    ]

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=100,
        bottomMargin=50,
    )
    doc.build(elements)
    buffer.seek(0)

    # Mescla com PDF base
    overlay_pdf = PdfReader(buffer)
    for i, page in enumerate(template_pdf.pages):
        if i < len(overlay_pdf.pages):
            PageMerge(page).add(overlay_pdf.pages[i]).render()

    # Salva PDF final
    nome_associado = slugify(associado.user.get_full_name())
    # 🔥 Lista de anos em atraso
    anos_em_atraso = "-".join(
        str(a.anuidade.ano) for a in anuidades_em_aberto
    )
    # ✅ Nome do PDF
    pdf_name = f"Notificacao_anuidades_{associado.id}_{nome_associado}_{anos_em_atraso}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    query = urlencode({'pdf_url': pdf_url})
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?{query}&tipo=cobranca")
# -----------------------------------------------------------------------------------------------------------

# =======================================================================================================
# GERAR COBRANÇA/NOTIFICAÇÃO EM LOTE
import zipfile
import re

def slugify_filename(nome):
    return re.sub(r'\W+', '_', nome.strip().lower())

def gerar_cobrancas_em_lote(request):
    hoje = datetime.now()
    ano_atual = hoje.year
    data_hoje = hoje.strftime('%d/%m/%Y')

    # Caminho do template base
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/cobranca_anuidades.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("Modelo base da cobrança não foi encontrado.", status=404)
    template_pdf = PdfReader(template_path)

    # Verifica se tem anuidade do ano atual
    try:
        anuidade_atual = AnuidadeModel.objects.get(ano=ano_atual)
    except AnuidadeModel.DoesNotExist:
        return HttpResponse("Valor da anuidade atual não foi configurado.", status=404)

    valor_anuidade_atual = anuidade_atual.valor_anuidade

    # Diretório de saída
    output_dir = os.path.join(settings.MEDIA_ROOT, 'documentos', 'cobrancas_em_lote')
    os.makedirs(output_dir, exist_ok=True)

    arquivos_gerados = []

    for associado in AssociadoModel.objects.all():
        anuidades_em_aberto = AnuidadeAssociado.objects.filter(
            associado=associado,
            pago=False,
            anuidade__ano__lt=ano_atual
        ).select_related('anuidade')

        if not anuidades_em_aberto.exists():
            continue

        total_anuidades_em_aberto = anuidades_em_aberto.count()
        valor_total_cobrado = valor_anuidade_atual * total_anuidades_em_aberto

        lista_anuidades = " - ".join([
            f"<strong>{a.anuidade.ano}</strong>: R$ {a.anuidade.valor_anuidade:.2f}"
            for a in anuidades_em_aberto
        ])

        associacao = associado.associacao
        municipio = associacao.municipio.upper() if associacao.municipio else "CIDADE NÃO DEFINIDA"
        local_data = f"{municipio}, {data_hoje}."
        nome_presidente = associacao.presidente.user.get_full_name()
        assinatura = f"{nome_presidente}<br/>Presidente da Associação<br/>APAPESC"

        texto = f"""
        <br/><br/>
        Prezado(a) <strong>{associado.user.get_full_name()}</strong>,<br/><br/>

        Realizamos uma análise em nosso sistema e identificamos que, até o momento, não localizamos o seu nome nas listagens de pagamentos das seguintes anuidades:

        {lista_anuidades}. Também não identificamos o envio de comprovantes de pagamento para os anos mencionados. Se os pagamentos já foram realizados, por gentileza, envie os comprovantes para que possamos atualizar sua situação.<br/><br/>

        Caso ainda não tenha efetuado os pagamentos, o valor a ser considerado é com base na anuidade vigente(atual) ({ano_atual}), que é no valor de <strong>R$ {valor_anuidade_atual:.2f}</strong> por ano em aberto.

        Sendo assim, o valor total das anuidade(es) em aberto é de: <strong>R$ {valor_total_cobrado:.2f}</strong>.<br/><br/>

        <strong>OBS:</strong> As anuidades computadas nesse documento são de anos <font color='red'><strong>anteriores</strong></font> ao ano vigente (atual).<br/><br/>

        Entre em contato para verificar as formas de pagamento. <strong>Facilitamos para voçê!</strong> <br/><br/>

        <em>Agradecemos por sua atenção. A sua contribuição fortalece a associação e nos permite seguir prestando apoio e serviços aos associados.</em>
        """


        # Estilos PDF
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontName='Times-Bold',
            fontSize=14,
            alignment=TA_CENTER,
            leading=20,
            spaceBefore=27,
            textColor=colors.black,
        )
        style_normal = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=12,
            leading=17,
            alignment=TA_JUSTIFY,
            spaceBefore=0,
        )
        style_assinatura = ParagraphStyle(
            'Assinatura',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=12,
            leading=18,
            alignment=TA_CENTER,
            spaceBefore=10,
        )
        style_presidente = ParagraphStyle(
            'Presidente',
            parent=styles['Normal'],
            fontName='Times-Bold',
            fontSize=12,
            alignment=2,
            leading=16,
            spaceBefore=10,
            textColor=colors.grey,
        )

        # Cria PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=100, bottomMargin=50)
        elements = [
            Spacer(1, 61),
            Paragraph(nome_presidente, style_presidente),
            Spacer(1, 35),
            Paragraph("ANUIDADES EM ABERTO", style_title),
            Spacer(1, 1),
            Paragraph(texto, style_normal),
            Spacer(1, 7),
            Paragraph(local_data, style_normal),
            Spacer(1, 7),
            Paragraph(assinatura, style_assinatura),
        ]
        doc.build(elements)
        buffer.seek(0)

        overlay_pdf = PdfReader(buffer)
        template_pdf = PdfReader(template_path)
        for i, page in enumerate(template_pdf.pages):
            if i < len(overlay_pdf.pages):
                PageMerge(page).add(overlay_pdf.pages[i]).render()

        nome_formatado = slugify_filename(associado.user.get_full_name())
        pdf_name = f"cobranca_{nome_formatado}_{ano_atual}.pdf"
        pdf_path = os.path.join(output_dir, pdf_name)
        PdfWriter(pdf_path, trailer=template_pdf).write()
        arquivos_gerados.append(pdf_path)

    # Cria o zip
    zip_path = os.path.join(settings.MEDIA_ROOT, 'documentos', f"cobrancas_anuidades_{ano_atual}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in arquivos_gerados:
            zipf.write(file, os.path.basename(file))

    # Redireciona para download
    zip_url = f"{settings.MEDIA_URL}documentos/cobrancas_anuidades_{ano_atual}.zip"
    return redirect(zip_url)



# =======================================================================================================
# GERAR RECIBO DE ENTRADA EXTRA ASSOCIADO
# app_automacoes/views.py

def gerar_recibo_entrada_extra(request, entrada_id):
    entrada = get_object_or_404(EntradaFinanceira, id=entrada_id, status_pagamento='pago')

    servico = getattr(entrada, 'entrada_servico_extra', None)
    if not servico or not servico.extra_associado:
        return HttpResponse("Esta entrada não está vinculada a um serviço de extra associado.", status=400)

    extra = servico.extra_associado
    associacao = entrada.associacao

    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/recibo_servico_extra.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para o Recibo de Entrada Extra não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)
    buffer = BytesIO()
    data_hoje = datetime.now().strftime('%d/%m/%Y')

    # Último pagamento
    pagamento = entrada.pagamentos.order_by('-data_pagamento').first()
    if not pagamento:
        return HttpResponse("Nenhum pagamento registrado para essa entrada.", status=400)

    data_pagamento = pagamento.data_pagamento.strftime('%d/%m/%Y')

    # Estilos
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=14,
        alignment=TA_CENTER,
        leading=28,
        spaceBefore=40,
        textColor=colors.black,
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
    )
    style_assinatura = ParagraphStyle(
        'Assinatura',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,
        alignment=TA_CENTER,
        spaceBefore=10,
    )
    style_presidente = ParagraphStyle(
        'Presidente',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        alignment=2,
        leading=16,
        spaceBefore=10,
        textColor=colors.grey,
    )
    nome_presidente = associacao.presidente.user.get_full_name()

    municipio = associacao.municipio.upper() if associacao.municipio else "CIDADE NÃO DEFINIDA"
    local_data = f"{municipio}, {data_hoje}."

    # Texto
    texto = (
        f"Recebemos de <strong>{extra.nome_completo}</strong>, "
        f"inscrito no CPF sob o nº <strong>{extra.cpf}</strong>, "
        f"a importância de <strong>R$ {entrada.valor_pagamento:.2f}</strong> "
        f"(referente ao serviço de <strong>{entrada.tipo_servico.nome}</strong>), "
        f"pelo qual, registramos a confirmação de pagamento na data de <strong>{data_pagamento}</strong>. "
        f"<br/><br/>Este pagamento foi efetuado à <strong>{associacao.razao_social}</strong>, "
        f"inscrita no CNPJ sob o nº {associacao.cnpj}, com sede na {associacao.logradouro}, nº {associacao.numero}, "
        f"{associacao.bairro}, {associacao.municipio or 'Município não informado'}/{associacao.uf}. "
        f"<br/><br/><i>Salientamos o nosso agradecimento pela contratação dos nossos serviços e pela confiação no nosso trabalho. "
        f" Estaremos sempre à sua disposição! Conte Gente.</i>"
    )

    assinatura = (
        f"{nome_presidente}<br/>"
        f"Presidente da Associação"
    )

    # Elementos do PDF
    elements = [
        Spacer(1, 50),
        Paragraph(nome_presidente, style_presidente),
        Spacer(1, 35),
        Paragraph("RECIBO DE SERVIÇO PRESTADO", style_title),
        Spacer(1, 20),
        Paragraph(texto, style_normal),
        Spacer(1, 24),
        Paragraph(local_data, style_normal),
        Spacer(1, 20),
        Paragraph(assinatura, style_assinatura),
    ]

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=120,
        bottomMargin=50,
    )
    doc.build(elements)
    buffer.seek(0)

    overlay_pdf = PdfReader(buffer)
    for index, template_page in enumerate(template_pdf.pages):
        if index < len(overlay_pdf.pages):
            overlay_page = overlay_pdf.pages[index]
            PageMerge(template_page).add(overlay_page).render()

    pdf_name = f"recibo_servico_extra_{extra.id}_{entrada.id}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    query_string = urlencode({'pdf_url': pdf_url})
    return redirect(f"{reverse('app_automacoes:pagina_acoes_entrada', args=[entrada.id])}?{query_string}&tipo=servico_extra")



# =======================================================================================================
# GERAR CARTEIRINHA APAPESC ASSOCIADO
# app_automacoes/views.py

def gerar_carteirinha_apapesc(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)
    associacao = associado.associacao

    # Caminho para o PDF de template
    # Busca o modelo de carteirinha
    template_instance = CarteirinhaAssociadoModel.objects.first()
    if not template_instance or not template_instance.pdf_base:
        return HttpResponse("Modelo de carteirinha não disponível.", status=404)

    template_path = template_instance.pdf_base.path
    template_pdf = PdfReader(template_path)

    # Carrega o template

    buffer = BytesIO()


    # Inicia o canvas sobre buffer
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 8)

    # Cor dourada clara
    dourado_claro = Color(218/255, 165/255, 32/255)
    c.setFillColor(dourado_claro)

    # Dados do associado
    nome = associado.user.get_full_name()
    profissao = associado.profissao or ''
    data_filiacao = associado.data_filiacao.strftime('%d/%m/%Y') if associado.data_filiacao else ''
    cpf = associado.cpf or ''
    rgp = associado.rgp or ''
    primeiro_registro = associado.primeiro_registro.strftime('%d/%m/%Y') if associado.primeiro_registro else ''
    municipio = associado.municipio_circunscricao or ''
    estado = associado.uf or ''

    # Deslocamento e posições ajustadas
    x_base = 25     # 2.5cm da esquerda
    y = 758         # Subiu 70 pontos

    # Renderiza as linhas
    c.drawString(x_base, y, f"{nome}")
    y -= 22
    c.drawString(x_base, y, f"{profissao}")
    c.drawString(x_base + 180, y, f"{data_filiacao}")
    y -= 23
    c.drawString(x_base, y, f"{cpf}")
    c.drawString(x_base + 80, y, f"{rgp}")
    c.drawString(x_base + 180, y, f"{primeiro_registro}")
    y -= 25
    c.drawString(x_base, y, f"{municipio}")
    c.drawString(x_base + 200, y, f"{estado}")
    y -= 20
        
    c.showPage()
    c.save()

    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)

    # Mescla o conteúdo gerado com o template
    for i, page in enumerate(template_pdf.pages):
        if i < len(overlay_pdf.pages):
            PageMerge(page).add(overlay_pdf.pages[i]).render()

    # Salvar arquivo final
    output_path = os.path.join(settings.MEDIA_ROOT, f'documentos/carteirinha_{associado.id}.pdf')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    PdfWriter(output_path, trailer=template_pdf).write()

    # URL para acesso
    pdf_url = f"{settings.MEDIA_URL}documentos/carteirinha_{associado.id}.pdf"
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?pdf_url={pdf_url}")
    


# GERAR PROCURAÇÃO ADMINISTRATIVA
def gerar_procuracao_administrativa(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)

    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/procuracao_administrativa.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Procuração Administrativa não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)

    # Buffer em memória para o conteúdo dinâmico
    buffer = BytesIO()

    # Definindo estilos personalizados
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=17,
        alignment=1,  # Centralizado
        leading=32,  # Espaçamento entre as linhas do título
        spaceBefore=80,  # Espaçamento antes do título
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=4,  # Justificado
    )
    style_assinatura = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=1,  # Justificado
    )
    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Texto da declaração
    texto1 = (
        f"<strong>OUTORGANTE(S)</strong>: <strong>{associado.user.get_full_name()}</strong>, brasileira, "
        f"profissão, {associado.profissao}, estado civil, {associado.estado_civil}, CPF nº {associado.cpf}, "
        f"RG nº {associado.rg_numero}, com residência e domicílio estabelecido á {associado.logradouro}, "
        f"nº {associado.numero}, {associado.complemento}, {associado.bairro}, {associado.municipio} -"
        f" {associado.uf} {associado.cep}. "
        f"<br /><br /><strong>OUTORGADOS</strong>: <strong>CRISTIANI JORDANI DOS SANTOS RAMOS</strong>, "
        f"brasileira, casada, advogada, inscrição na OAB/SC sob o número 51.410, inscrita no CPF 853.801.219-34, "
        f"<strong>SAMARA IZILDA CORREA DOS SANTOS</strong>,  brasileira, divorciada,"
        f"advogada, inscrição na OAB/SC sob o número 51.380, inscrita no CPF 027.034.419-59, integrantes do "
        f"escritório JORDANI & SANTOS Advogados Associados."
    )
    texto2 = (
        f"<strong>PODERES:</strong> Pelo presente instrumento, o(a) outorgante confere plenos poderes à <strong>APAPESC - "
        f"Associação de Assistência aos Servidores Públicos de Santa Catarina</strong> e/ou seus representantes legais, "
        f"para que, em seu nome, representem seus interesses junto a qualquer órgão da Administração Pública Direta ou Indireta, "
        f"entidades autárquicas, fundacionais, ou quaisquer repartições governamentais, em todas as esferas federativas."
        
        f"<br />Esta procuração concede poderes amplos, gerais e ilimitados, inclusive os da cláusula <em>“ad judicia et extra”</em>, "
        f"permitindo aos outorgados propor requerimentos, firmar declarações, prestar informações, protocolar documentos, "
        f"solicitar diligências e praticar todos os atos necessários para assegurar os direitos do(a) associado(a), "
        f"em especial <strong>para fins de requerimento administrativo do benefício do Seguro Defeso</strong>, junto ao INSS, MAPA, MTE "
        f"e demais órgãos competentes."
        
        f"<br /><br />A presente outorga autoriza ainda a obtenção de informações, consultas em sistemas oficiais, assinatura de formulários, "
        f"declarações de elegibilidade, e realização de todos os procedimentos pertinentes ao andamento e conclusão do referido pedido de benefício."

        f"<br /><br />Os poderes ora conferidos poderão ser exercidos em conjunto ou separadamente por quaisquer dos representantes da APAPESC, "
        f"com faculdade de substabelecimento, no todo ou em parte, a quem melhor aprouver, com ou sem reserva de poderes."

        f"<br /><br />Esta procuração é válida por prazo indeterminado, até que seja formalmente revogada pelo(a) outorgante."
    )


    # Local e data
    local_data = f"{associado.reparticao.municipio_sede}, {data_atual}."
    assinatura = (
        "____________________________________________________________________<br/>"
        f"<strong>{associado.user.get_full_name()}</strong><br/>"
        f"CPF: {associado.cpf}<br/>"
    )

    # Elementos do PDF
    elements = [
        Paragraph("PROCURAÇÃO ADMINISTRATIVA", style_title),
        Spacer(1, 1),
        Paragraph(texto1, style_normal),
        Spacer(1, 5),
        Paragraph(texto2, style_normal),
        Spacer(1, 5),
        Paragraph(local_data, style_normal),
        Spacer(1, 10),
        Paragraph(assinatura, style_assinatura),
    ]

    # Criando o documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=85,
        leftMargin=85,
        topMargin=140,
        bottomMargin=40,
    )

    doc.build(elements)

    # Mesclando o conteúdo dinâmico com o template
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)

    # **Ajuste Importante:**
    # O número de páginas do template e o overlay_pdf deve ser gerenciado com cuidado.
    for index, template_page in enumerate(template_pdf.pages):
        if index < len(overlay_pdf.pages):
            overlay_page = overlay_pdf.pages[index]
            PageMerge(template_page).add(overlay_page).render()

    # Salvando o PDF final
    pdf_name = f"procuracao_administrativa_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Preparando o redirecionamento
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?pdf_url={pdf_url}")
# ======================================================================================================

# Autorizacao Direitos de Imagem

def gerar_autorizacao_direitos_imagem(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)

    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/autorizacao_direito_imagem.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Autorização de uso e Direitos de Imagem.", status=404)

    template_pdf = PdfReader(template_path)

    # Buffer em memória para o conteúdo dinâmico
    buffer = BytesIO()

    # Definindo estilos personalizados
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=17,
        alignment=1,  # Centralizado
        leading=32,  # Espaçamento entre as linhas do título
        spaceBefore=100,  # Espaçamento antes do título
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=4,  # Justificado
    )
    style_assinatura = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=1,  # Justificado
    )
    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Texto da Autorização
    texto1 = (
        f"<strong>ATORIZAÇÂO</strong>: Eu, <strong>{associado.user.get_full_name()}</strong>, brasileira, "
        f"profissão, {associado.profissao}, estado civil, {associado.estado_civil}, CPF nº {associado.cpf}, "
        f"RG nº {associado.rg_numero}, com residência e domicílio estabelecido á {associado.logradouro}, "
        f"nº {associado.numero}, {associado.complemento}, {associado.bairro}, {associado.municipio} -"
        f" {associado.uf} {associado.cep}. "
        f"<br /><br /><strong>AUTORIZO</strong>: <strong> A ASSOCIAÇÃO APAPESC</strong>: "

    )
    texto2 = (
        f"<strong>AUTORIZAÇÃO:</strong> O(A) associado(a) autoriza expressamente a <strong>APAPESC - Associação de "
        f"Assistência aos Servidores Públicos de Santa Catarina</strong> a utilizar sua imagem, voz e nome para fins institucionais, "
        f"incluindo, mas não se limitando a, postagens em redes sociais, inserções em campanhas de divulgação, matérias jornalísticas, "
        f"artigos e publicações no site oficial da associação, bem como em materiais impressos ou digitais voltados à comunicação com os associados "
        f"e à promoção das atividades realizadas pela associação. "
        f"<br /><br />A presente autorização é concedida de forma gratuita, por prazo indeterminado e em caráter irrevogável, abrangendo o uso em "
        f"todo o território nacional e internacional, sem que isso implique em qualquer ônus, remuneração ou compensação ao(à) associado(a). "
        f"<br /><br />A APAPESC compromete-se a utilizar a imagem de forma ética, respeitosa e alinhada aos princípios estatutários da associação, "
        f"preservando sempre a honra, reputação e dignidade do(a) associado(a)."
    )


    # Local e data
    local_data = f"{associado.reparticao.municipio_sede}, {data_atual}."
    assinatura = (
        "____________________________________________________________________<br/>"
        f"<strong>{associado.user.get_full_name()}</strong><br/>"
        f"CPF: {associado.cpf}<br/>"
    )

    # Elementos do PDF
    elements = [
        Paragraph("AUTORIZAÇÃO DE USO E DIREITOS IMAGEM", style_title),
        Spacer(1, 10),
        Paragraph(texto1, style_normal),
        Spacer(1, 10),
        Paragraph(texto2, style_normal),
        Spacer(1, 10),
        Paragraph(local_data, style_normal),
        Spacer(1, 24),
        Paragraph(assinatura, style_assinatura),
    ]

    # Criando o documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=85,
        leftMargin=85,
        topMargin=140,
        bottomMargin=40,
    )

    doc.build(elements)

    # Mesclando o conteúdo dinâmico com o template
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)

    # **Ajuste Importante:**
    # O número de páginas do template e o overlay_pdf deve ser gerenciado com cuidado.
    for index, template_page in enumerate(template_pdf.pages):
        if index < len(overlay_pdf.pages):
            overlay_page = overlay_pdf.pages[index]
            PageMerge(template_page).add(overlay_page).render()

    # Salvando o PDF final
    pdf_name = f"autorizacao_direito_imagem_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Preparando o redirecionamento
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?pdf_url={pdf_url}")
# ======================================================================================================    

# AUTORIZAÇÂO ACESSO GOV
def gerar_autorizacao_acesso_gov(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)

    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/autorizacao_acesso_gov.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Autorização Acesso e Gestão conta Gov.", status=404)

    template_pdf = PdfReader(template_path)

    # Buffer em memória para o conteúdo dinâmico
    buffer = BytesIO()

    # Definindo estilos personalizados
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=17,
        alignment=1,  # Centralizado
        leading=32,  # Espaçamento entre as linhas do título
        spaceBefore=100,  # Espaçamento antes do título
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=4,  # Justificado
    )
    style_assinatura = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=1,  # Justificado
    )
    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Texto da Autorização acesso e Gestão conta Gov
    texto1 = (
        f"<strong>ATORIZAÇÂO</strong>: Eu, <strong>{associado.user.get_full_name()}</strong>, brasileira, "
        f"profissão, {associado.profissao}, estado civil, {associado.estado_civil}, CPF nº {associado.cpf}, "
        f"RG nº {associado.rg_numero}, com residência e domicílio estabelecido á {associado.logradouro}, "
        f"nº {associado.numero}, {associado.complemento}, {associado.bairro}, {associado.municipio} -"
        f" {associado.uf} {associado.cep}. "
        f"<br /><br /><strong>AUTORIZO</strong>: <strong>INTEGRANTES ADMINISTRATIVOS DA APAPESC</strong>: "

    )
    texto2 = (
    f"<strong>AUTORIZAÇÃO DE ACESSO À CONTA GOV.BR:</strong> O(A) associado(a) autoriza formalmente a <strong>APAPESC - "
    f"Associação de Assistência aos Servidores Públicos de Santa Catarina</strong>, por meio de seus representantes administrativos, "
    f"a realizar acesso e gestão das informações disponíveis na plataforma <strong>Gov.br</strong>, vinculadas ao seu CPF, exclusivamente "
    f"para fins de representação institucional, acompanhamento de benefícios, atualização cadastral, instrução de processos administrativos "
    f"ou judiciais e demais procedimentos relacionados aos direitos e interesses do(a) associado(a) perante órgãos públicos. "
    f"<br /><br />A presente autorização inclui, mas não se limita a: geração e uso de senhas temporárias, acesso a históricos de benefícios, "
    f"envio e recebimento de documentos por meio da conta Gov.br, assinatura digital de requerimentos e consultas em nome do(a) associado(a). "
    f"<br /><br />A autorização é concedida por prazo indeterminado, podendo ser revogada a qualquer tempo por manifestação expressa do(a) associado(a), "
    f"e se destina exclusivamente ao exercício de atividades relacionadas à atuação da associação em defesa dos interesses do(a) outorgante. "
    f"<br /><br />A APAPESC compromete-se a utilizar as credenciais de forma ética, segura, e dentro dos limites legais, respeitando os princípios "
    f"da confidencialidade, privacidade e boa-fé."
)



    # Local e data
    local_data = f"{associado.reparticao.municipio_sede}, {data_atual}."
    assinatura = (
        "____________________________________________________________________<br/>"
        f"<strong>{associado.user.get_full_name()}</strong><br/>"
        f"CPF: {associado.cpf}<br/>"
    )

    # Elementos do PDF
    elements = [
        Paragraph("AUTORIZAÇÃO DE ACESSO EM CONTA GOV", style_title),
        Spacer(1, 10),
        Paragraph(texto1, style_normal),
        Spacer(1, 10),
        Paragraph(texto2, style_normal),
        Spacer(1, 10),
        Paragraph(local_data, style_normal),
        Spacer(1, 24),
        Paragraph(assinatura, style_assinatura),
    ]

    # Criando o documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=85,
        leftMargin=85,
        topMargin=140,
        bottomMargin=40,
    )

    doc.build(elements)

    # Mesclando o conteúdo dinâmico com o template
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)

    # **Ajuste Importante:**
    # O número de páginas do template e o overlay_pdf deve ser gerenciado com cuidado.
    for index, template_page in enumerate(template_pdf.pages):
        if index < len(overlay_pdf.pages):
            overlay_page = overlay_pdf.pages[index]
            PageMerge(template_page).add(overlay_page).render()

    # Salvando o PDF final
    pdf_name = f"autorizacao_acesso_gov_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Preparando o redirecionamento
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?pdf_url={pdf_url}")
# ======================================================================================================        


# Declaração de Desfiliação
def gerar_declaracao_desfiliacao(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)

    # Caminho para o PDF de template
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/declaracao_desfiliacao.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para a Autorização Acesso e Gestão conta Gov.", status=404)

    template_pdf = PdfReader(template_path)

    # Buffer em memória para o conteúdo dinâmico
    buffer = BytesIO()

    # Definindo estilos personalizados
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=17,
        alignment=1,  # Centralizado
        leading=32,  # Espaçamento entre as linhas do título
        spaceBefore=100,  # Espaçamento antes do título
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=4,  # Justificado
    )
    style_assinatura = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Espaçamento entre linhas
        alignment=1,  # Justificado
    )
    # Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # Texto do pedido de desfiliação
    texto1 = (
        f"<strong>EU</strong>: <strong>{associado.user.get_full_name()}</strong>, brasileira, "
        f"profissão, {associado.profissao}, estado civil, {associado.estado_civil}, CPF nº {associado.cpf}, "
        f"RG nº {associado.rg_numero}, com residência e domicílio estabelecido á {associado.logradouro}, "
        f"nº {associado.numero}, {associado.complemento}, {associado.bairro}, {associado.municipio} -"
        f" {associado.uf} {associado.cep}. "
        f"<br /><br /><strong>DECLARO</strong>: "
    )
    
    texto2 = (
        f"<strong>DECLARAÇÃO DE DESFILIAÇÃO VOLUNTÁRIA:</strong> Eu, <strong>{associado.user.get_full_name()}</strong>, "
        f"associado(a) da <strong>APAPESC - Associação de Assistência aos Servidores Públicos de Santa Catarina</strong>, "
        f"venho por meio desta, manifestar de forma livre, consciente e espontânea minha decisão de <strong>me desligar do quadro de associados da APAPESC</strong>."
        f"<br /><br />Declaro estar ciente de que, a partir desta data, deixarei de usufruir dos benefícios, serviços e representações oferecidos pela associação, "
        f"renunciando voluntariamente a qualquer vínculo associativo ativo."
        f"<br /><br />Solicito que sejam adotadas as providências administrativas necessárias para formalização da minha desfiliação, "
        f"bem como a atualização dos registros internos da associação."
        f"<br /><br />Reitero que esta decisão é tomada por minha livre e espontânea vontade, sem qualquer coação ou influência de terceiros, "
        f"e reconheço o trabalho e a importância da APAPESC na defesa dos interesses dos servidores públicos catarinenses."
    )




    # Local e data
    local_data = f"{associado.reparticao.municipio_sede}, {data_atual}."
    assinatura = (
        "____________________________________________________________________<br/>"
        f"<strong>{associado.user.get_full_name()}</strong><br/>"
        f"CPF: {associado.cpf}<br/>"
    )

    # Elementos do PDF
    elements = [
        Paragraph("DECLARAÇÃO DE DESFILIAÇÃO", style_title),
        Spacer(1, 10),
        Paragraph(texto1, style_normal),
        Spacer(1, 10),
        Paragraph(texto2, style_normal),
        Spacer(1, 10),
        Paragraph(local_data, style_normal),
        Spacer(1, 24),
        Paragraph(assinatura, style_assinatura),
    ]

    # Criando o documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=85,
        leftMargin=85,
        topMargin=140,
        bottomMargin=40,
    )

    doc.build(elements)

    # Mesclando o conteúdo dinâmico com o template
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)

    # **Ajuste Importante:**
    # O número de páginas do template e o overlay_pdf deve ser gerenciado com cuidado.
    for index, template_page in enumerate(template_pdf.pages):
        if index < len(overlay_pdf.pages):
            overlay_page = overlay_pdf.pages[index]
            PageMerge(template_page).add(overlay_page).render()

    # Salvando o PDF final
    pdf_name = f"declaracao_desfiliacao_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    # Preparando o redirecionamento
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?pdf_url={pdf_url}")
# ======================================================================================================            

def gerar_direitos_deveres(request, associado_id):
    associado = AssociadoModel.objects.get(id=associado_id)
    associacao = associado.associacao

    # PDF base
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf/direitos_deveres.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)
    buffer = BytesIO()

    # Estilos
    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle(
        'NormalJustified',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=16,
        alignment=4,  # Justificado
    )


    style_title = ParagraphStyle(
        'TitlePadrao',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=17,
        alignment=1,
        leading=32,
        spaceBefore=20,  # Usual nas páginas seguintes
    )

    style_assinatura = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        alignment=1,  # Centralizado
    )

    data_atual = datetime.now().strftime('%d/%m/%Y')
    local_data = f"{associado.reparticao.municipio_sede}, {data_atual}."
    assinatura = (
        "____________________________________________________________________<br/>"
        f"<strong>{associado.user.get_full_name()}</strong><br/>"
        f"CPF: {associado.cpf}<br/>"
    )

    # Dividindo em 3 partes (como textos)
    texto1 = (
        f"<strong>REGRAMENTO INTERNO – DIREITOS, DEVERES E COMPROMISSOS ASSOCIATIVOS</strong><br/><br/>"
        f"<strong>Seja muito bem-vindo(a) à Associação dos Pescadores e Agricultores – APAPESC!</strong><br/><br/>"
        f"Sua participação é fundamental para o fortalecimento da nossa comunidade. Ao se unir à APAPESC, "
        f"você passa a fazer parte de um grupo que acredita no desenvolvimento sustentável, na cooperação entre os associados "
        f"e no protagonismo da pesca e da agricultura familiar.<br/><br/>"
        f"A coletividade é o nosso alicerce. Trabalhamos juntos para garantir dignidade, reconhecimento e apoio real aos trabalhadores do mar e do campo.<br/><br/>"
        f"<strong>O Que Fazemos por Você</strong><br/>"
        f"✅ <strong>Defesa dos Interesses Coletivos:</strong> Buscamos políticas públicas e soluções práticas que beneficiem pescadores e agricultores, "
        f"como incentivos, acesso a crédito, regularização de documentos e infraestrutura adequada.<br/>"
        f"✅ <strong>Assistência Junto a Órgãos Governamentais:</strong> Ajudamos na emissão de documentos obrigatórios (RGP, TIE, CAEPF, licenças e registros), "
        f"intermediação com o MAPA, Receita Federal, Marinha, INSS e outros órgãos.<br/>"
        f"✅ <strong>Suporte Jurídico e Administrativo:</strong> Oferecemos apoio em processos como o Seguro Defeso, regularização previdenciária, impugnações, petições e orientações jurídicas especializadas.<br/>"
        f"✅ <strong>Fortalecimento da Classe:</strong> A união dos associados é nossa força. Quanto mais organizados estivermos, maior será nossa representatividade diante das autoridades e dos desafios cotidianos."
    )


    texto2 = (
        f"<strong>Direitos dos Associados</strong><br/>"
        f"• Receber orientações e assistência técnica nos processos de regularização.<br/>"
        f"• Ter acesso ao suporte jurídico, institucional e documental disponibilizado pela Associação.<br/>"
        f"• Participar de campanhas, projetos e iniciativas promovidas pela APAPESC.<br/>"
        f"• Ter seus interesses coletivos representados em órgãos públicos e espaços de decisão.<br/>"
        f"• Ser tratado com respeito, atenção e igualdade.<br/><br/>"

        f"<strong>Deveres e Regramentos Internos</strong><br/>"
        f"🔹 <strong>Cordialidade e Respeito:</strong> Zelar pela boa convivência entre os membros. Condutas ofensivas, desrespeitosas ou de cunho discriminatório não são adequadas e podem gerar consequências a ser deliberadas pela administração da APAPESC.<br/>"
        f"🔹 <strong>Documentos em Boa Qualidade:</strong> É responsabilidade do associado entregar documentos solicitados em bom estado, coloridos e legíveis, preferencialmente escaneados em papelaria.<br/>"
        f"🔹 <strong>Comunicação Oficial e Grupos da APAPESC:</strong> Os associados devem permanecer nos grupos oficiais de WhatsApp:<br/>"
        f"&nbsp;&nbsp;&nbsp;&nbsp;• Grupo Administrativo da APAPESC (obrigatório)<br/>"
        f"&nbsp;&nbsp;&nbsp;&nbsp;• Grupo Família APAPESC (opcional)<br/>"
        f"&nbsp;&nbsp;&nbsp;&nbsp;• Grupo de Envio de Fotos (opcional)<br/><br/>"
        f"📵 É proibida a divulgação de conteúdos ofensivos ou que possam ferir a integridade de outros membros.<br/>"
        f"🔐 Jamais compartilhe seus dados pessoais ou senhas com terceiros desconhecidos.<br/><br/>"
        f"🔹 <strong>Participação Ativa:</strong> Os associados devem participar, sempre que possível e dentro das suas condições, das reuniões, eventos, mutirões e ações promovidas pela associação.<br/>"
        f"🔹 <strong>Atualização Cadastral:</strong> É dever do associado manter seus dados e documentos atualizados, comunicar mudança de endereço, celular e realizar recadastramento quando solicitado."
    )


    texto3 = (
        f"<strong>Anuidade Associativa</strong><br/>"
        f"🔹 <strong>Exercício e Vencimento:</strong> A anuidade vigora entre 1º de janeiro e 31 de dezembro de cada ano. "
        f"Preferencialmente, ela deve ser paga na data de filiação. No entanto, isso não é um obstáculo! Sempre podem ser concedidos prazos e condições especiais, mediante conversa com a administração.<br/><br/>"
        f"🔹 <strong>Anuidade do Ano Atual:</strong> Pode ser paga a qualquer momento dentro do exercício.<br/>"
        f"🔹 <strong>Anuidade Atrasada (Exercícios Anteriores):</strong> Caso a anuidade de anos anteriores não tenha sido quitada, ela será considerada em atraso. Neste caso, será aplicada a mesma tarifa vigente do ano atual. Exemplo: se a anuidade de 2024 (R$230,00) não for paga até 31/12/2024, em 2025 o valor cobrado será o da anuidade atual.<br/><br/>"
        f"🔹 <strong>Regularização e Notificações:</strong> Associados com anuidades em aberto poderão ser notificados para apresentar comprovante de pagamento ou negociar condições de regularização diretamente com a administração. Casos específicos serão analisados individualmente, com atenção às possibilidades de cada associado.<br/><br/>"

        f"<strong>Compromisso Coletivo</strong><br/>"
        f"Na APAPESC, buscamos o fortalecimento da pesca artesanal e da agricultura familiar de forma organizada, legal e sustentável.<br/>"
        f"Nossa missão é cuidar de quem vive da pesca e do campo, com justiça, respeito e dignidade.<br/><br/>"
        f"💙 Conte conosco. Crescemos juntos.<br/><br/>"
        f"APAPESC – Por uma pesca legal, sustentável e valorizada.<br/><br/>"
        f"{local_data}<br/><br/>"
        f"{assinatura}"
    )


    # Criando o conteúdo
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=85,
        leftMargin=85,
        topMargin=60,  # ⬅️ Margem superior reduzida
        bottomMargin=50,
    )

    elements = [
        Spacer(1, 120),  # Primeira página mais abaixo
        Paragraph("REGRAMENTO INTERNO - DIREITOS E DEVERES", style_title),
        Spacer(1, 12),
        Paragraph(texto1, style_normal),

        PageBreak(),
        Spacer(1, 60),  # ⬅️ Espaço no topo da segunda página
        Paragraph("REGRAMENTO INTERNO - DIREITOS E DEVERES", style_title),
        Spacer(1, 12),
        Paragraph(texto2, style_normal),

        PageBreak(),
        Spacer(1, 60),  # ⬅️ Espaço no topo da terceira página
        Paragraph("REGRAMENTO INTERNO - DIREITOS E DEVERES", style_title),
        Spacer(1, 12),
        Paragraph(texto3, style_normal),
    ]



    # Gera o PDF em memória
    doc.build(elements)
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)

    # Mescla o conteúdo com o template base
    for i, template_page in enumerate(template_pdf.pages):
        if i < len(overlay_pdf.pages):
            PageMerge(template_page).add(overlay_pdf.pages[i]).render()

    # Salva o resultado final
    pdf_name = f"direitos_deveres_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?pdf_url={pdf_url}")
# ----------------------------------------------------------------------------------------------------

# Retirada de Documentos


def gerar_retirada_documentos(request, associado_id):
    associado = get_object_or_404(AssociadoModel, id=associado_id)
    associacao = associado.associacao
    # 📄 Template base da declaração
    template_path = os.path.join(settings.MEDIA_ROOT, 'pdf', 'retirada_documentos.pdf')
    if not os.path.exists(template_path):
        return HttpResponse("O PDF base para retirada de documentos não foi encontrado.", status=404)

    template_pdf = PdfReader(template_path)
    buffer = BytesIO()

    # 🎨 Estilos
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=17,
        alignment=1,
        leading=28,
        spaceBefore=30,
    )
    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=16,
        alignment=4,
    )
    style_assinatura = ParagraphStyle(
        'Assinatura',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        alignment=1,
    )
    style_presidente = ParagraphStyle(
        'Presidente',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        alignment=2,
        leading=16,
        spaceBefore=10,
        textColor=colors.grey,
    )
    nome_presidente = associacao.presidente.user.get_full_name()    

    # 📅 Data atual
    data_atual = datetime.now().strftime('%d/%m/%Y')

    # ✍️ Conteúdo
    paragrafo_inicial = (
        f"<strong>{associado.user.get_full_name()}</strong>, CPF: {associado.cpf}, RG: {associado.rg_numero}, "
        f"residente em {associado.logradouro}, {associado.numero} - {associado.bairro}, "
        f"{associado.municipio}/{associado.uf}, vem por meio desta declarar que retirei os seguintes documentos:"
    )

    lista_documentos = (
        "<br/><br/>"
        "[ ] LICENÇA<br/>"
        "[ ] RG<br/>"
        "[ ] CPF<br/>"
        "[ ] RGP<br/>"
        "[ ] Carteirinha da APAPESC<br/>"
        "[ ] TIE<br/>"
        "[ ] Seguro DPEM<br/><br/>"
        "[ ] _____________________________________________<br/>"
        "[ ] _____________________________________________<br/>"
        "[ ] _____________________________________________<br/><br/>"
    )

    aviso = (
        "<strong>Declaro estar ciente</strong> de que a retirada dos documentos acima mencionados é de minha total responsabilidade, "
        "assumindo a guarda e conservação dos mesmos. Estou ciente de que a APAPESC não se responsabiliza pela perda, dano ou extravio "
        "dos documentos após esta retirada."
    )

    local_data = f"{associado.reparticao.municipio_sede}, {data_atual}"
    assinatura = (
        "____________________________________________________________________<br/>"
        f"<strong>{associado.user.get_full_name()}</strong><br/>"
        f"CPF: {associado.cpf}<br/>"
    )

    # 📄 Elementos a renderizar
    elements = [
        Spacer(1, 50),
        Paragraph(nome_presidente, style_presidente),
        Paragraph("DECLARAÇÃO DE RETIRADA DE DOCUMENTOS", style_title),
        Spacer(1, 10),
        Paragraph(paragrafo_inicial, style_normal),
        Spacer(1, 12),
        Paragraph(lista_documentos, style_normal),
        Spacer(1, 8),
        Paragraph(aviso, style_normal),
        Spacer(1, 24),
        Paragraph(local_data, style_normal),
        Spacer(1, 30),
        Paragraph(assinatura, style_assinatura),
    ]

    # 📄 Criando PDF overlay
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=85,
        rightMargin=85,
        topMargin=115,
        bottomMargin=40,
    )
    doc.build(elements)

    # 📎 Mesclando com o template
    buffer.seek(0)
    overlay_pdf = PdfReader(buffer)

    for idx, template_page in enumerate(template_pdf.pages):
        if idx < len(overlay_pdf.pages):
            PageMerge(template_page).add(overlay_pdf.pages[idx]).render()

    # 💾 Salvando o PDF final
    pdf_name = f"retirada_documentos_{associado.user.get_full_name().replace(' ', '_')}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'documentos', pdf_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    PdfWriter(pdf_path, trailer=template_pdf).write()

    # 🔗 Redireciona com link para download
    pdf_url = f"{settings.MEDIA_URL}documentos/{pdf_name}"
    return redirect(f"{reverse('app_automacoes:pagina_acoes', args=[associado.id])}?pdf_url={pdf_url}")
