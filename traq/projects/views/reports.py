import json
from traq.utils import UnicodeWriter
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.timezone import utc
from django.contrib.auth.models import User
from ..forms import ReportIntervalForm
from ..models import Project, Component
from traq.tickets.models import Ticket
from django.contrib.auth.decorators import permission_required
from traq.tickets.templatetags.tickets import tickettimepretty

@permission_required('projects.can_view_all')
def mega(request):
    form, interval = _intervalHelper(request)
    users = list(User.objects.all().order_by("username"))
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

@permission_required('projects.can_view_all')
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

@permission_required('projects.can_view_all')
def component(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form, interval = _intervalHelper(request)
    components = project.components(interval=interval)
    # queries in loop...stupid but on reports, I don't care
    for comp in components:
        comp.tickets = list(Ticket.objects.filter(component=comp))
        for t in comp.tickets:
            t.times = t.totalTimes(interval)


    # render as CSV?
    if request.GET.get('format', '') == 'csv':
        response = HttpResponse(content_type='text/csv')
        filename = "report-" + datetime.now().strftime("%Y-%m-%d") + ".csv"
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        csv = UnicodeWriter(response)
        csv.writerow([interval[0].strftime("%Y-%m-%d"), interval[1].strftime("%Y-%m-%d")])
        csv.writerow(['Component', '#', 'Ticket', 'Status', 'Assigned', 'Total Hours', 'Billable Hours', 'Release'])
        for comp in components:
            csv.writerow([comp.name, '','','','', tickettimepretty(comp.total), tickettimepretty(comp.billable)])
            for ticket in comp.tickets:
                csv.writerow(['', unicode(ticket.pk), ticket.title, ticket.status.name, '' if ticket.assigned_to is None else ticket.assigned_to.username, tickettimepretty(ticket.times['total']), tickettimepretty(ticket.times['billable']), ticket.release])
         
        return response

    # render normally
    return render(request, 'projects/reports/component.html', {
        'project': project,
        'components': components,
        'form': form,
        'queries': connection.queries,
    })

@permission_required('projects.can_view_all')
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
    if request.GET.get('submit'):
        form = ReportIntervalForm(request.GET)
        if form.is_valid():
            interval = (form.cleaned_data['start'], form.cleaned_data['end'])

    if interval == ():
        now = datetime.utcnow().replace(tzinfo=utc)
        earlier = now - timedelta(days=30)
        interval = (earlier, now)

        if not request.GET.get('submit'):
            form = ReportIntervalForm(initial={"start": interval[0], "end": interval[1]})
    return form, interval
