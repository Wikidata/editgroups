from django import template
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.filter(is_safe=True)
def isadmin(user):
    if not user or not user.is_authenticated():
        return False
    try:
        socialauth = user.social_auth.get()
        userinfo = socialauth.extra_data.get('userinfo', {})
        return 'delete' in userinfo.get('rights', [])
    except ObjectDoesNotExist:
        return False

