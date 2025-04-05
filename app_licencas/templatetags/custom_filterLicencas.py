
from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr_name):
    """Permite acessar atributos dinamicamente no template"""
    return getattr(obj, attr_name, '')

