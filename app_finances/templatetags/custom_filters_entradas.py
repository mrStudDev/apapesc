from django import template
from babel.numbers import format_currency
register = template.Library()

@register.filter
def mul(value, arg):
    """ Multiplica dois valores """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0  # Retorna 0 se houver erro



register = template.Library()

@register.filter
def format_real(value):
    """ Formata um número para o padrão brasileiro R$ 9.999,99 """
    try:
        value = float(value)  # Garante que o valor é numérico
        return format_currency(value, 'BRL', locale='pt_BR')  # Usa Babel para formatação correta
    except (ValueError, TypeError):
        return "R$ 0,00"
