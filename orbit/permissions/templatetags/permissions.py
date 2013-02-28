from django import template
from django.core.exceptions import PermissionDenied
from .. import decorators

register = template.Library()

@register.filter
def can_edit(user, instance):
    can = decorators.can_edit(instance=instance)
    try:
        can.check(None, user, instance)
    except PermissionDenied as e:
        return False

    return True
