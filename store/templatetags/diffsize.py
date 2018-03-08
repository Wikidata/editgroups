from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def diffsize(edit):
    if type(edit) == int:
        diffsize = edit
    else:
        diffsize = edit['newlength'] - edit['oldlength']
    diffstr = '+%d' % diffsize if diffsize > 0 else str(diffsize)
    if diffsize >= 500:
        span = '<strong class="mw-plusminus-pos">%s</strong>' % diffstr
    elif diffsize > 0:
        span = '<span class="mw-plusminus-pos">%s</span>' % diffstr
    elif diffsize == 0:
        span = '<span>%s</span>' % diffstr
    elif diffsize > -500:
        span = '<span class="mw-plusminus-neg">%s</span>' % diffstr
    else:
        span = '<strong class="mw-plusminus-neg">%s</strong>' % diffstr
    return mark_safe(span)
