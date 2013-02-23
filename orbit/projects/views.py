from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from .forms import ProjectForm, ComponentForm
from .models import Project, Component
from ..tickets.models import Ticket

def all(request):
    projects = Project.objects.all()
    return render(request, 'projects/all.html', {
        'projects': projects,
    })

def detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    tickets = project.tickets()
    components = Component.objects.withTimes(project=project)
    return render(request, 'projects/detail.html', {
        'project': project,
        'tickets': tickets,
        'queries': connection.queries,
        'components': components,
    })
    

def create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            form.instance.createDefaultComponents()
            return HttpResponseRedirect(reverse("projects-all"))
    else:
        form = ProjectForm()

    return render(request, 'projects/create.html', {
        'form': form,
    })


def components_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ComponentForm(request.POST, project=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
    else:
        form = ComponentForm(project=project)

    return render(request, 'projects/components_create.html', {
        'project': project,
        'form': form,
    })
