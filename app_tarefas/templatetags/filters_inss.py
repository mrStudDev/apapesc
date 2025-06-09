from django import template

register = template.Library()

@register.filter(name='get_item')  # Note o name='get_item' aqui
def get_item_filter(dictionary, key):
    return dictionary.get(key, 0)