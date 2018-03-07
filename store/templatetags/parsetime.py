from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import dateutil.parser

register = template.Library()

@register.filter(is_safe=True)
def parsetime(timestamp):
    d = dateutil.parser.parse(timestamp)
    return d
