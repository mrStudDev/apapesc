# app_tarefas/templatetags/filter_producao_anual.py
from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, None)
