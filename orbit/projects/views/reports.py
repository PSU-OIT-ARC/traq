import json
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from django.utils.timezone import utc
from ..forms import ProjectForm, ComponentForm, ReportIntervalForm
from ..models import Project, Component
from orbit.tickets.models import Ticket
from orbit.tickets.forms import QuickTicketForm
from orbit.permissions.decorators import can_view, can_edit, can_create

def grid(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return HttpResponse("<img src='/static/img/mharvey.gif'/>")

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
        #start_of_month = datetime(year=now.year, month=now.month, day=1)
        earlier = now - timedelta(days=30)
        interval = (earlier, now)

        if not request.GET:
            form = ReportIntervalForm(initial={"start": interval[0], "end": interval[1]})
    return form, interval
