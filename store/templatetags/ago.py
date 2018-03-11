from django import template
from datetime import datetime
from datetime import timedelta
from django.utils.timesince import timesince
from pytz import UTC

register = template.Library()

@register.filter
def ago(date):
    if date.tzinfo is None:
        date = datetime.utcfromtimestamp(int(date.strftime("%s")))
    now = datetime.now(UTC)
    try:
        difference = now - date
    except Exception as e:
        print(e)
        return date

    if difference <= timedelta(minutes=1):
        return 'just now'
    elif now.day != date.day:
        return date
    age = timesince(date).split(', ')[0]
    return '{} ago'.format(age)
