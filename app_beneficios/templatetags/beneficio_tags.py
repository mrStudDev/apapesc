from django import template
from app_beneficios.models import ControleBeneficioModel  # Adjust the import path as needed
from django.utils import timezone

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retorna o valor de um dicionário para uma chave específica"""
    return dictionary.get(key, '')

@register.filter(name='attr')
def attr(field, args):
    attrs = {}
    for pair in args.split(","):
        if ":" in pair:
            key, value = pair.split(":", 1)
        elif "=" in pair:
            key, value = pair.split("=", 1)
        else:
            continue
        attrs[key.strip()] = value.strip()
    return field.as_widget(attrs=attrs)

@register.simple_tag
def get_beneficio_aplicado(associado):
    hoje = timezone.now().date()
    return ControleBeneficioModel.objects.filter(
        associado=associado,
        beneficio__data_inicio__lte=hoje,
        beneficio__data_fim__gte=hoje,
    ).exclude(status_pedido='ARQUIVADO').order_by('-beneficio__data_inicio').first()
