from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def isadmin(user):
    socialauth = user.social_auth.get()
    userinfo = socialauth.extra_data.get('userinfo', {})
    return 'delete' in userinfo.get('rights', [])

