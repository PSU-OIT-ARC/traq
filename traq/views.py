from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('accounts-profile'))

    return render(request, 'home.html', {
        'show_logo': True,
    })
