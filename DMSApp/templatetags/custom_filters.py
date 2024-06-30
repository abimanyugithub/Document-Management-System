from django import template
from urllib.parse import quote_plus
from django.db.models.fields.files import FieldFile
from django.utils.dateformat import format
import datetime  # Ensure datetime is imported correctly
from django.db.models import CharField, TextField
import re
from django.utils.text import slugify

register = template.Library()

@register.filter
def get_field_value(obj, attr_name):
    value = getattr(obj, attr_name, None)
    if isinstance(value, FieldFile):
        return value.url
    if isinstance(value, datetime.datetime):
        return format(value, 'd-m-Y')
    return value

@register.filter
def custom_slugify(value):
    return quote_plus(value)
    # Use Django's slugify to create a base slug
    # return slugify(value)

@register.filter
def get_field_value_exclude_url(obj, attr_name):
    return getattr(obj, attr_name, None)
