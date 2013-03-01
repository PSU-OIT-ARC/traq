import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from ..forms import ProjectForm, ComponentForm
from ..models import Project, Component
from orbit.tickets.models import Ticket
from orbit.tickets.forms import QuickTicketForm
from orbit.permissions.decorators import can_view, can_edit, can_create

def grid(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return HttpResponse("<img src='/static/img/mharvey.gif'/>")

def component(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    components = project.components()
    return render(request, 'projects/reports/component.html', {
        'project': project,
        'components': components,
    })

def invoice(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    components = project.components()
    return render(request, 'projects/reports/invoice.html', {
        'project': project,
        'components': components,
    })
