from django import template
from app_beneficios.models import ControleBeneficioModel

register = template.Library()

@register.simple_tag
def get_controle(beneficio, associado):
    try:
        return ControleBeneficioModel.objects.get(beneficio=beneficio, associado=associado)
    except ControleBeneficioModel.DoesNotExist:
        return None
