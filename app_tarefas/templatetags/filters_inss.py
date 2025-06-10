from django import template

register = template.Library()

@register.filter(name='get_item')  # Note o name='get_item' aqui
def get_item_filter(dictionary, key):
    return dictionary.get(key, 0)



MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',
    4: 'Abril', 5: 'Maio', 6: 'Junho',
    7: 'Julho', 8: 'Agosto', 9: 'Setembro',
    10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}

@register.filter
def nome_do_mes(numero_mes):
    return MESES_PT.get(numero_mes, f"Mês {numero_mes}")