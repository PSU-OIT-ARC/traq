from urllib import urlencode
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from djangocas.views import login as cas_login
from . import checkers

# This is the base class for the can_* decorators. Subclasses can override
# runCheck() and return the value of any checkers.can_* function
class can_do(object):
    def __init__(self, model=None):
        self.model = model

    # return False is access is denied, True is access is allowed, or None for
    # a 404
    def runCheck(self, *args, **kwargs):
        user = args[0].user
        return checkers.can_do(user)

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            can_proceed = self.runCheck(*args, **kwargs)
            request = args[0]
            user = request.user
            if can_proceed == False:
                # if their logged in, give the perm defined error.
                # but if they are not logged in, redirect to the login page
                if user.is_authenticated():
                    raise PermissionDenied("Access denied")
                else:
                    params = urlencode({REDIRECT_FIELD_NAME: request.get_full_path()})
                    return HttpResponseRedirect(reverse(cas_login) + '?' + params)
            elif can_proceed == None:
                raise Http404("Fail in can_do decorator")

            return f(*args, **kwargs)

        return wrapper
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
            return None

        return self.checker.__func__(user, instance)

# use the same logic for editing, but pass the buck to checkers.can_edit
class can_edit(can_view):
    checker = checkers.can_edit

#check if user can create specific model
class can_create(can_do):
    checker = checkers.can_create
    
    def runCheck(self, *args, **kwargs):
        user = args[0].user
        return self.checker.__func__(user, self.model)
