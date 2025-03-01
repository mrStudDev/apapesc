from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Permite acessar dicionários dentro do template Django."""
    return d.get(key, None) if isinstance(d, dict) else None
