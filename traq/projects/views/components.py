import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from ..forms import ProjectForm, ComponentForm
from ..models import Project, Component

@permission_required('projects.add_component')
def create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ComponentForm(request.POST, project=project, created_by=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
    else:
        form = ComponentForm(project=project, created_by=request.user)

    return render(request, 'projects/components/create.html', {
        'project': project,
        'form': form,
    })

@permission_required('projects.change_component')
def edit(request, component_id):
    component = get_object_or_404(Component, pk=component_id)
    project = component.project
    if request.method == "POST":
        form = ComponentForm(request.POST, instance=component, project=project, created_by=component.created_by)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
    else:
        form = ComponentForm(instance=component, project=project, created_by=component.created_by)

    return render(request, 'projects/components/create.html', {
        'project': project,
        'form': form,
    })
