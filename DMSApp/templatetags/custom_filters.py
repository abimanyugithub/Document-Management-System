from django import template
from urllib.parse import quote_plus
from django.db.models.fields.files import FieldFile

register = template.Library()

@register.filter
def get_field_value(obj, attr_name):
    value = getattr(obj, attr_name, None)
    if isinstance(value, FieldFile):
        return value.url
    return value

@register.filter
def custom_slugify(value):
    return quote_plus(value)

@register.filter
def get_field_value_exclude_url(obj, attr_name):
    return getattr(obj, attr_name, None)