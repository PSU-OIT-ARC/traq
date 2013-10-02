from django.core.exceptions import PermissionDenied
from django.db.models import Q
from traq.projects.models import Project

LOGIN_GROUPS = ("arc", "pdx09876", 'arcclient')
STAFF_GROUP = "arcstaff"
CLIENT_CAN_CREATE = ['ToDo']

# these can_* functions simply return true or false of a user is allowed to do
# stuff

def can_do(user):
    return user.is_authenticated()

def can_create(user, model):
    if user.groups.filter(Q(name=STAFF_GROUP) | Q(name='arc')).exists():
        return True
    elif model.__name__ in CLIENT_CAN_CREATE:
        return True
    return False

def can_view(user, instance):
    return True

def can_edit(user, instance):
    # If you are a member of the STAFF group, then you can edit anything.
    # Because Django doesn't cache the groups that a user belongs to,
    # we create a little flag on the user object indicating if the user can
    # edit anything. This avoids trips to the database on
    # subsequent calls to can_edit
    if getattr(user, 'can_edit_anything', None) is None:
        if user.groups.filter(name=STAFF_GROUP).exists():
            user.can_edit_anything = True
        else:
            user.can_edit_anything = False

    if user.can_edit_anything:
        return True

    # you can edit something assigned to you
    if getattr(instance, 'assigned_to_id', None) == user.pk:
        return True

    # you can edit something created by you
    if getattr(instance, 'created_by_id', None) == user.pk:
        return True

    return False

def can_login(groups):
    return (set(LOGIN_GROUPS) & set(groups)) != set()
