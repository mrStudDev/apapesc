# app_embarcacoes/templatetags/custom_filters_embarcacao.py
from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    return form[field_name]

@register.filter
def get_attr(obj, attr_name):
    """Permite acessar atributos dinamicamente no template"""
    return getattr(obj, attr_name, None)