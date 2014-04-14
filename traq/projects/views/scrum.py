from datetime import date, timedelta, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.db.models import Count
from ..models import Project, Milestone
from traq.tickets.models import Ticket
from traq.tickets.filters import TicketFilterSet
from traq.todos.filters import ToDoFilterSet, ToDoPriorityFilterSet
from traq.todos.models import ToDo
from traq.permissions.decorators import can_view_project

@can_view_project
def dashboard(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    sess_sprint = "sprint_end%d" % project.pk
    sprint_end = request.session.get(sess_sprint, project.current_sprint_end)
    ticket_filterset = TicketFilterSet(request.GET, queryset=project.tickets(), project_id = project_id)
    todo_list = ToDo.objects.prefetch_related('tickets')
    
    q = request.GET.get('q', '')
    if request.GET.get('q'):
        tickets = ticket_filterset.qs.filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q))
        todos = todo_list.filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q), due_on=sprint_end, is_deleted=False)
    else:
        tickets = ticket_filterset.qs.order_by("-status__importance", "-global_order", "-assigned_to", "-priority__rank")
        todos = todo_list.filter(project=project, due_on=sprint_end, is_deleted=False)
    tickets =tickets.filter(due_on=sprint_end)
    if project.current_sprint_end is not None:
        upcoming = todo_list.filter(Q(project=project), Q(due_on__gt=datetime.today())| Q(due_on__isnull=True), is_deleted=False).exclude(due_on=sprint_end).annotate(null_pos=Count('due_on')).order_by('-null_pos','due_on')
    else:
        upcoming = None
    components = project.components()
    work = project.latestWork(10)
    milestones = Milestone.objects.filter(project=project)
    if sprint_end is not None:
        next = sprint_end + timedelta(days=14) 
        prev = sprint_end - timedelta(days=14)
    else:
        next = None
        prev = None
    tix_completed = tickets.filter(Q(status__name='Completed')|Q(status__name='Closed')).count() 
    todos_completed = todos.filter(Q(status__name='Completed')|Q(status__name='Closed')).count() 
    return render(request, "projects/dashboard.html", {
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
        'tix_completed': tix_completed,
        'todos_completed': todos_completed,
    })

@can_view_project
@permission_required('todos.change_todo')
def backlog(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    #todos with no estimates 
    todo_filterset = ToDoPriorityFilterSet(request.GET, queryset=ToDo.objects.filter(project=project, is_deleted=False, status_id=1, estimate__isnull=True), project_id=project_id)
    todos = todo_filterset
    q = request.GET.get('q', None) 
    if q is not None:
        todos = todos.qs.filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q))
        
    return render(request, 'projects/backlog.html', {
        'todos': todos,
        'project': project,
        'filterset': todo_filterset,
        })

@can_view_project
@permission_required('todos.change_todo')
def sprint_planning(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    #todos with no tickets 
    todo_filterset = ToDoPriorityFilterSet(request.GET, queryset=ToDo.objects.filter(project=project, is_deleted=False, status_id=1, tickets__isnull=True), project_id=project_id)
    todos = todo_filterset
    q = request.GET.get('q', None) 
    if q is not None:
        todos = todos.qs.filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q))
        
    return render(request, 'projects/backlog.html', {
        'todos': todos,
        'project': project,
        'filterset': todo_filterset,
        })

@can_view_project
def scrum(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    sess_sprint = "sprint_end%d" % project.pk
    sprint_end = request.session.get(sess_sprint, project.current_sprint_end)
    return render(request, "projects/scrum.html",{
        'project': project,
        'sprint_end': sprint_end,
        })
    
    
def which_sprint(request, project_id):
    project = get_object_or_404(Project,pk= project_id)
    if request.method == "POST":
        end = request.POST.get('current_sprint_end', project.current_sprint_end)
        sprint = "sprint_end%d" % project.pk
        request.session[sprint] = datetime.strptime(end, "%Y-%m-%d").date() 
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
