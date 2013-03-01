from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from . import checkers

# This is the base class for the can_* decorators. Subclasses can override
# runCheck() and return the value of any checkers.can_* function
class can_do(object):
    def __init__(self, model=None):
        self.model = model

    def runCheck(self, *args, **kwargs):
        user = args[0].user
        return checkers.can_do(user)

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            if self.runCheck(*args, **kwargs) == False:
                return HttpResponseRedirect("/")

            return f(*args, **kwargs)

        return wrapper


class can_create(can_do):
    pass

# for the can_view and can_edit decorators, assume the second argument to the
# view function is the model's primary key (the first argument is of course,
# the request object). Look up the model instance, and pass that along to the
# designated checker function (the class variable called "checker")
class can_view(can_do):
    checker = checkers.can_view

    def runCheck(self, *args, **kwargs):
        user = args[0].user
        pk = args[1]

        try:
            instance = self.model.objects.get(pk=pk)
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned) as e:
            raise PermissionDenied("Fail")

        return self.checker.__func__(user, instance)

# use the same logic for editing, but pass the buck to checkers.can_edit
class can_edit(can_view):
    checker = checkers.can_edit
