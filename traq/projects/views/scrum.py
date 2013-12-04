from datetime import date, timedelta, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from ..models import Project, Milestone
from traq.tickets.models import Ticket
from traq.tickets.filters import TicketFilterSet
from traq.todos.models import ToDo


@permission_required('projects.can_view_all', raise_exception=True)
def dashboard(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    ticket_filterset = TicketFilterSet(request.GET, queryset=project.tickets(), project_id = project_id)
    q = request.GET.get('contains', '')
    if request.GET.get('due_on') == 'a':
        tickets = ticket_filterset.qs.order_by("-due_on")
    elif request.GET.get('due_on') == 'd':
        tickets = ticket_filterset.qs.order_by("due_on")
    elif request.GET.get('contains'):
        tickets = ticket_filterset.qs.filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q))
    else:
        tickets = ticket_filterset.qs.order_by("-status__importance", "-global_order", "-priority__rank")
    
    sess_sprint = "sprint_end%d" % project.pk
    sprint_end = request.session.get(sess_sprint, project.current_sprint_end)
    tickets =tickets.filter(due_on=sprint_end)
    todo_list = ToDo.objects.prefetch_related('tickets')
    todos = todo_list.filter(project=project, due_on=sprint_end)
    upcoming = todo_list.filter(project=project, due_on__gt=project.current_sprint_end)
    components = project.components()
    work = project.latestWork(10)
    milestones = Milestone.objects.filter(project=project)
    next = sprint_end + timedelta(days=14)
    prev = sprint_end - timedelta(days=14)
    
    return render(request, "projects/scrum_detail.html", {
        'project': project,
        'tickets': tickets,
        'components': components,
        'work': work,
        'milestones': milestones,
        'filterset': ticket_filterset,
        'todos': todos,
        'sprint_end': sprint_end,
        'next': next,
        'prev':prev,
        'upcoming': upcoming,
    })
