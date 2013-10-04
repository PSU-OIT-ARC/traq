from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from traq.permissions import STAFF_GROUP

def home(request):
    if request.user.is_authenticated():
        if request.user.groups.filter(name=STAFF_GROUP):
            return HttpResponseRedirect(reverse('projects-all'))
        return HttpResponseRedirect(reverse('accounts-profile'))

    return render(request, 'home.html', {
        'show_logo': True,
    })
