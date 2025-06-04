# app_documentos/templatetags/documento_extras.py
import os
from django import template

register = template.Library()

@register.filter
def extensao(arquivo_field):
    if not arquivo_field:
        return ''
    nome_arquivo = str(arquivo_field.name)
    return os.path.splitext(nome_arquivo)[-1].replace('.', '').upper()
