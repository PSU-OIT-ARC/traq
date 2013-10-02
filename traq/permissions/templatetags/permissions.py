from django import template
from django.core.exceptions import PermissionDenied
from .. import checkers

register = template.Library()

# use in a template like:
# user|can_edit:some_model_instance
@register.filter
def can_view(user, instance):
    return checkers.can_view(user, instance)

@register.filter
def can_edit(user, instance):
    return checkers.can_edit(user, instance)

@register.filter
def can_create(user, model):
    return checkers.can_create(user, model)
