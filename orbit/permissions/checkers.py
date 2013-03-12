from django.core.exceptions import PermissionDenied
USER_GROUP = "arc"
STAFF_GROUP = "arcstaff"

# these can_* functions simply return true or false of a user is allowed to do
# stuff

def can_do(user):
    return user.is_authenticated()

def can_create(user, model):
    return can_do(user)

def can_view(user, instance):
    return can_do(user)

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

