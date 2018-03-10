from django import template
from datetime import timedelta

register = template.Library()

@register.filter()
def secondsduration(seconds):
    if type(seconds) != int:
        return ''
    delta = timedelta(seconds=seconds)
    return delta
