from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

def home(request):
    user_agent = request.META.get("HTTP_USER_AGENT", None)
    ip = request.META.get('REMOTE_ADDR', None)
    return render(request, 'home.html', {
        'user_agent': user_agent,
        'ip': ip,
    })
