from django import template

register = template.Library()

@register.filter
def to_i(value):
    return int(value)
