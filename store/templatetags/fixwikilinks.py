from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re

register = template.Library()

r = re.compile('href="/wiki/')

@register.filter()
def fixwikilinks(html):
    return r.sub('href="https://www.wikidata.org/wiki/', str(html))
