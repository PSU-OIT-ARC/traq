from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from . import checkers

# This is the base class for the can_* decorators. Subclasses can mix in the
# can_* checkers in the checkers module. They can also implement the check
# method and do some pre or post checks
class can_do(object):
    def __init__(self, model):
        self.model = model

    # subclasses can implement this
    def check(self, user, *args, **kwargs):
        pass

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            request = args[0]
            user = request.user

            try:
                self.check(user, *args, **kwargs)
            except PermissionDenied:
                return HttpResponseRedirect("/")

            return f(*args, **kwargs)

        return wrapper


class can_create(can_do, checkers.can_create):
    pass

# for the can_view and can_edit decorators, assume the second argument to the
# view function is the model's primary key (the first argument is of course,
# the request object). Look up the model instance, and pass that along to the
# super classes. The can_do decorator will ignore it, but the checker.can_*
# function will use it.
class can_view(can_do, checkers.can_view):
    def check(self, user, *args, **kwargs):
        pk = args[1]
        try:
            instance = self.model.objects.get(pk=pk)
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned) as e:
            raise PermissionDenied("Fail")

        super(can_view, self).check(user, instance)

# use the same logic for editing, but pass the buck to checkers.can_edit
class can_edit(can_view, checkers.can_edit):
    pass
