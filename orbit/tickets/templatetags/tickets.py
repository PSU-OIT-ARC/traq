import markdown2
from datetime import time, timedelta
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def frommarkdown(value):
    """Converts a string from markdown to HTML"""
    return mark_safe(markdown2.markdown(value, safe_mode='escape'))

@register.filter()
def tickettime(value):
    """Converts a time or timedelta object to a string like '5h 22m'"""
    if value is None:
        return u"0h 0s"
    if isinstance(value, time):
        return value.strftime("%Hh %Mm")
    if isinstance(value, timedelta):
        days = value.days
        minutes, seconds = divmod(value.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours + days*24
        return u'%dh %dm' % (hours, minutes)

@register.filter()
def tickettimepretty(value):
    """Converts a time or timedelta object to a string like '11:22'"""
    if value is None:
        return u"0"
    if isinstance(value, time):
        return value.strftime("%H:%M")
    if isinstance(value, timedelta):
        days = value.days
        minutes, seconds = divmod(value.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours + days*24
        if hours == seconds == 0:
            return u'0'
        return u'%d:%02d' % (hours, minutes)
