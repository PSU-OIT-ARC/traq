from django.core.exceptions import PermissionDenied
STAFF = "arcstaff"

class can_do(object):
    def check(self, user):
        if user.is_anonymous():
            raise PermissionDenied("No access")

class can_create(can_do):
    def check(self, user, model):
        super(can_create, self).check(user)

class can_view(can_do):
    def check(self, user, instance):
        super(can_view, self).check(user)

class can_edit(can_do):
    def check(self, user, instance):
        super(can_edit, self).check(user)
        # If you are a member of the STAFF group, then you can edit anything.
        # Because Django doesn't cache the groups that a user belongs to,
        # we create a little flag on the user object indicating if the user can
        # edit anything. This avoids trips to the database on
        # subsequent calls to can_edit
        if getattr(user, 'can_edit_anything', None) is None:
            if user.groups.filter(name=STAFF).exists():
                user.can_edit_anything = True
                return
            else:
                user.can_edit_anything = False

        # you can edit something assigned to you
        if getattr(instance, 'assigned_to_id', None) == user.pk:
            return

        # you can edit something created by you
        if getattr(instance, 'created_by_id', None) == user.pk:
            return

        raise PermissionDenied("No access")

