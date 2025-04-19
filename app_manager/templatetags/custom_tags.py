from django import template
from app_beneficios.models import ControleBeneficioModel, BeneficioModel

register = template.Library()

@register.simple_tag

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
