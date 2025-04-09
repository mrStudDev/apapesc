from urllib.parse import urlparse
from django import template

register = template.Library()

@register.filter
def urlparse(value, attr="netloc"):
    try:
        parsed = urlparse(value if value.startswith("http") else f"https://{value}")
        result = getattr(parsed, attr)
        return result or value  # fallback: mostra o original se não achar
    except Exception:
        return value