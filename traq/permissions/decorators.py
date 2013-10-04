from urllib import urlencode
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from djangocas.views import login as cas_login
from traq.projects.models import Project
from . import checkers

def can_view_project(fn):
    """
    This decorator assumes the second argument to the view is the pk of a
    project. It uses that to check if the request.user has permission to see
    the project
    """
    def wrapper(*args, **kwargs):
        request = args[0]
        user = request.user
        pk = args[1]
        project = Project.objects.get(pk=pk)
        if user in project.clients.all() or user.has_perm("projects.can_view_all"):
            return fn(*args, **kwargs)

        # they can access the page
        if user.is_authenticated():
            raise PermissionDenied("Access denied")
        else:
            # they're just not logged in
            params = urlencode({REDIRECT_FIELD_NAME: request.get_full_path()})
            return HttpResponseRedirect(reverse(cas_login) + '?' + params)

    return wrapper
