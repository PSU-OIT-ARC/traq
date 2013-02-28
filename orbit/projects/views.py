import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from .forms import ProjectForm, ComponentForm
from .models import Project, Component
from ..tickets.models import Ticket
from ..tickets.forms import QuickTicketForm
from ..permissions.decorators import can_view, can_edit, can_create

def all(request):
    projects = Project.objects.all()
    return render(request, 'projects/all.html', {
        'projects': projects,
    })

@can_view(Project)
def detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    tickets = project.tickets()
    components = project.components()
    work = project.latestWork(10)
    tickets_json = project.tickets(to_json=True)
    if request.POST:
        form = QuickTicketForm(request.POST, project=project, created_by=request.user)
        if form.is_valid():
            messages.success(request, 'Ticket Created')
            form.save()
            request.session['ticket_initial_data'] = form.cleaned_data
            return HttpResponseRedirect(reverse('projects-detail', args=(project.pk,)))
    else:
        initial_data = request.session.get("ticket_initial_data", {})
        initial_data.pop("body", None)
        form = QuickTicketForm(initial=initial_data, project=project, created_by=request.user)
    return render(request, 'projects/detail.html', {
        'project': project,
        'tickets': tickets,
        'queries': connection.queries,
        'components': components,
        'form': form,
        'work': work,
        'tickets_json': tickets_json,
    })
    

@can_create(Project)
def create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, created_by=request.user)
        if form.is_valid():
            form.save()
            form.instance.createDefaultComponents()
            return HttpResponseRedirect(reverse("projects-all"))
    else:
        form = ProjectForm(created_by=request.user)

    return render(request, 'projects/create.html', {
        'form': form,
    })


@can_create(Component)
def components_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ComponentForm(request.POST, project=project, created_by=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
    else:
        form = ComponentForm(project=project, created_by=request.user)

    return render(request, 'projects/components_create.html', {
        'project': project,
        'form': form,
    })

@can_edit(Component)
def components_edit(request, component_id):
    component = get_object_or_404(Component, pk=component_id)
    project = component.project
    if request.method == "POST":
        form = ComponentForm(request.POST, instance=component, project=project, created_by=component.created_by)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
    else:
        form = ComponentForm(instance=component, project=project, created_by=component.created_by)

    return render(request, 'projects/components_create.html', {
        'project': project,
        'form': form,
    })

def reports_grid(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return HttpResponse("<img src='/static/img/mharvey.gif'/>")

def reports_component(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    components = project.components()
    return render(request, 'projects/reports_component.html', {
        'project': project,
        'components': components,
    })
