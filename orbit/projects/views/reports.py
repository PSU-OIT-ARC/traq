import json
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from django.utils.timezone import utc
from django.contrib.auth.models import User
from ..forms import ProjectForm, ComponentForm, ReportIntervalForm
from ..models import Project, Component
from orbit.tickets.models import Ticket
from orbit.tickets.forms import QuickTicketForm
from orbit.permissions.decorators import can_view, can_edit, can_create

def mega(request):
    form, interval = _intervalHelper(request)
    users = list(User.objects.all())
    projects = list(Project.objects.all())
    for user in users:
        user.projects = Project.objects.timeByUser(user, interval)
        user.totals = {"total": timedelta(0), "billable": timedelta(0), "non_billable": timedelta(0)}
        for project in user.projects:
            user.totals['total'] += project.total
            user.totals['billable'] += project.billable
            user.totals['non_billable'] += project.non_billable

    return render(request, 'projects/reports/mega.html', {
        'users': users,
        'projects': projects,
        'interval': interval,
        'form': form,
    })

def grid(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    # get all the people who have worked on this project
    form, interval = _intervalHelper(request)
    users = list(project.users())
    components = list(project.components())
    # for each user, for each component, figure out how much work they spent
    # query in a loop :(
    for user in users:
        user.components = Component.objects.timeByUser(project, user, interval=interval)
        user.totals = {"total": timedelta(0), "billable": timedelta(0), "non_billable": timedelta(0)}
        for comp in user.components:
            user.totals['total'] += comp.total
            user.totals['billable'] += comp.billable
            user.totals['non_billable'] += comp.non_billable

    return render(request, 'projects/reports/grid.html', {
        'project': project,
        'users': users,
        'components': components,
        'form': form,
        'interval': interval,
    })

def component(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form, interval = _intervalHelper(request)
    components = project.components(interval=interval)
    # queries in loop...stupid but on reports, I don't care
    for comp in components:
        comp.tickets = list(Ticket.objects.filter(component=comp))
        for t in comp.tickets:
            t.times = t.totalTimes(interval)

    return render(request, 'projects/reports/component.html', {
        'project': project,
        'components': components,
        'form': form,
        'queries': connection.queries,
    })

def invoice(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    form, interval = _intervalHelper(request)

    components = project.components(interval=interval)
    for comp in components:
        comp.breakdown = comp.invoiceBreakdown(interval)

    total_cost = project.totalCost(interval=interval)
    return render(request, 'projects/reports/invoice.html', {
        'project': project,
        'components': components,
        'total_cost': total_cost,
        'queries': connection.queries,
        'form': form,
        'interval': interval,
    })

def _intervalHelper(request):
    interval = ()
    if request.GET:
        form = ReportIntervalForm(request.GET)
        if form.is_valid():
            interval = (form.cleaned_data['start'], form.cleaned_data['end'])

    if interval == ():
        now = datetime.utcnow().replace(tzinfo=utc)
        earlier = now - timedelta(days=30)
        interval = (earlier, now)

        if not request.GET:
            form = ReportIntervalForm(initial={"start": interval[0], "end": interval[1]})
    return form, interval
