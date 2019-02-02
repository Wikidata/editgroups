from django import template
from django.urls import reverse
from django.utils.http import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def tagbutton(context, tag):
    if not tag or not tag.get('display_name'):
        return ''

    form = context.get('tagging_form') or {}
    current_tags = set(form.get('tags') or [])
    new_filter_form = dict(form.items())

    # Either the tag is currently selected
    tag_id = tag['id']
    if tag_id in current_tags:
        new_tags = current_tags - {tag_id}
    else:
        new_tags = current_tags | {tag_id}
    return set_get_param(context, 'tags', ','.join(new_tags))

@register.simple_tag(takes_context=True)
def set_get_param(context, key, value):
    request = context['request']
    new_get_params = dict(request.GET.items())
    if value:
        new_get_params[key] = value
    else:
        del new_get_params[key]
    if 'offset' in new_get_params:
        del new_get_params['offset']
    if 'limit' in new_get_params:
        del new_get_params['limit']
    new_url = request.path
    if new_get_params:
        new_url += '?' + urlencode(new_get_params)
    return new_url

