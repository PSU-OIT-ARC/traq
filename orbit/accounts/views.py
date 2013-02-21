from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    return render(request, "accounts/profile.html", {

    })
