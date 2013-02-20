from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from .forms import TicketForm
from .models import Ticket
from ..projects.models import Project

def detail(request, project_id, ticket_id):
    project = get_object_or_404(Project, pk=project_id)
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    return render(request, 'tickets/detail.html', {
        'project': project,
        'ticket': ticket,
    })
    

def create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = TicketForm(request.POST, project=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("tickets-detail", args=(project.pk, form.instance.pk)))
    else:
        form = TicketForm(project=project)

    return render(request, 'tickets/create.html', {
        'form': form,
    })

