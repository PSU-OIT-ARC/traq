from django.core.exceptions import PermissionDenied

STAFF = "arcstaff"

# This is the base class for the can_* decorators
# can_* decorators simply need to implement the 
# check(self, request, user, model, pk) method
# and raise an exception if permission is denied
class can_do(object):
    def __init__(self, model=None, instance=None):
        self.model = model
        self.instance = instance

    def check(self, request, user, instance):
        pass

    def __call__(self, f):
        def wrapper(request, pk=None):
            if self.instance is None:
                self.instance = self.model.objects.get(pk=pk)

            user = request.user
            if user.is_anonymous():
                raise PermissionDenied("No access")

            self.check(request, user, self.instance)

            return f(request, pk)

        return wrapper

class can_view(can_do):
    def check(self, request, user, instance):
        pass

class can_create(can_do):
    def check(self, request, user, instance):
        pass

class can_edit(can_do):
    def check(self, request, user, instance):
        if user.groups.filter(name=STAFF).exists():
            return

        if instance.created_by.pk != user.pk:
            raise PermissionDenied("No access")
