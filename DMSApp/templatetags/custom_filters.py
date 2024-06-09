from django import template
from urllib.parse import quote_plus

register = template.Library()

@register.filter
def get_field_value(obj, attr_name):
    return getattr(obj, attr_name, None)

@register.filter
def custom_slugify(value):
    return quote_plus(value)