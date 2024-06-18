from django import template
from urllib.parse import quote_plus
from django.db.models.fields.files import FieldFile
from django.utils.dateformat import format
import datetime  # Ensure datetime is imported correctly
from django.db.models import CharField, TextField

register = template.Library()

@register.filter
def get_field_value(obj, attr_name):
    value = getattr(obj, attr_name, None)
    if isinstance(value, FieldFile):
        return value.url
    if isinstance(value, datetime.datetime):
        return format(value, 'd-m-Y H:i')
    return value

@register.filter
def custom_slugify(value):
    return quote_plus(value)

@register.filter
def get_field_value_exclude_url(obj, attr_name):
    return getattr(obj, attr_name, None)
