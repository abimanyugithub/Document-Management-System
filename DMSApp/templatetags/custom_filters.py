from django import template

register = template.Library()

@register.filter
def get_field_value(obj, attr_name):
    return getattr(obj, attr_name, None)