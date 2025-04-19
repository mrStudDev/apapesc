from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Permite acessar dicionários dentro do template Django."""
    return d.get(key, None) if isinstance(d, dict) else None


@register.filter
def split(value, sep=","):
    return value.split(sep)

@register.filter
def index(sequence, position):
    try:
        return sequence[int(position)-1]
    except:
        return ""