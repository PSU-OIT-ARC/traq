import markdown2
from datetime import time, timedelta
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def frommarkdown(value):
    return mark_safe(markdown2.markdown(value, safe_mode='escape'))

@register.filter()
def tickettime(value):
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
    if value is None:
        return u"00:00"
    if isinstance(value, time):
        return value.strftime("%H:%M")
    if isinstance(value, timedelta):
        days = value.days
        minutes, seconds = divmod(value.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours + days*24
        return u'%02d:%02d' % (hours, minutes)
