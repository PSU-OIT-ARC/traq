from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from ..forms import ProjectForm
from ..models import Project, Milestone
from orbit.tickets.forms import QuickTicketForm
from orbit.permissions.decorators import can_do, can_view, can_edit, can_create
from orbit.utils import querySetToJSON

@can_do()
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
    tickets_json = querySetToJSON(tickets)
    milestones = Milestone.objects.filter(project=project)

    if request.POST:
        form = QuickTicketForm(request.POST, project=project, created_by=request.user)
        if form.is_valid():
            messages.success(request, 'Ticket Created')
            form.save()
            # save the ticket form data so the user doesn't have to reinput
            # everything again, if they want to create a similar ticket in the
            # future. Save the data on a per project basis (using the project's pk)
            if "quick_ticket_form" not in request.session:
                request.session['quick_ticket_form'] = {}
            request.session['quick_ticket_form'][project.pk] = form.cleaned_data
            # Django won't know to save the session because we are modifying a
            # 2D dictionary
            request.session.modified = True

            return HttpResponseRedirect(reverse('projects-detail', args=(project.pk,)))
    else:
        initial_data = request.session.get("quick_ticket_form", {}).get(project.pk, {})
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
        'milestones': milestones,
    })

@can_edit(Project)
def edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project, created_by=project.created_by)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("projects-all"))
    else:
        form = ProjectForm(instance=project, created_by=project.created_by)

    return render(request, 'projects/create.html', {
        'form': form,
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
