# app_documentos/templatetags/documento_extras.py
import os
from django import template
from app_documentos.models import Documento

register = template.Library()

@register.filter
def extensao(arquivo_field):
    if not arquivo_field:
        return ''
    nome_arquivo = str(arquivo_field.name)
    return os.path.splitext(nome_arquivo)[-1].replace('.', '').upper()


@register.simple_tag
def get_docs_padrao(*tipos):
    return Documento.objects.filter(
        repositorio_padrao=True,
        tipo_doc__tipo__in=tipos
    ).select_related('tipo_doc')

