from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from . import checkers

# This is the base class for the can_* decorators. Subclasses don't do
# anything but mixin the checkers.can_* classes. You pass in the model class
# when using the decorator on a view, and the second argument to the view is
# assumed to be the primary key of the object being edited, or viewed.

# Usage:
# @can_edit(Widget)
# def widget_edit(request, widget_id):
class can_do(object):
    def __init__(self, model):
        self.model = model

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            request = args[0]
            try:
                pk = args[1]
            except IndexError:
                pk = None

            # if there is a pk set, pass in the instance of the specific model,
            # otherwise, just send the model class
            if pk is not None:
                obj = self.model.objects.get(pk=pk)
            else:
                obj = self.model

            user = request.user

            try:
                self.check(user, obj)
            except PermissionDenied:
                return HttpResponseRedirect("/")

            return f(*args, **kwargs)

        return wrapper

class can_edit(can_do, checkers.can_edit):
    pass

class can_view(can_do, checkers.can_view):
    pass

class can_create(can_do, checkers.can_create):
    pass
