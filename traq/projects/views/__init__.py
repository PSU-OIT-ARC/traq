import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from datetime import date, timedelta, datetime
from django.db.models import Q

from traq.permissions.decorators import can_view_project
from traq.tickets.constants import TICKETS_PAGINATE_BY
from traq.utils import querySetToJSON, get_next_scrum_day

from ..forms import ProjectForm, ProjectSprintForm
from ..models import Project, Milestone
from ..views import scrum
from traq.todos.models import ToDo
from traq.todos.models import Ticket

# there's an annoying circular dependency between the ticket and project apps 
# so this import needs to be after project models are imported
from traq.tickets.filters import TicketFilterSet
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User



@permission_required('projects.can_view_all', raise_exception=True)
def all(request):
    projects_active = Project.objects.filter(status=Project.ACTIVE)
    projects_inactive = Project.objects.filter(status=Project.INACTIVE)
    
    return render(request, 'projects/all.html', {
        'projects_active': projects_active,
        'projects_inactive': projects_inactive,
    })

    
@can_view_project
def meta(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    try:
        target_completion = Milestone.objects.get(project=project, name="Target Completion Date").due_on
    except (Milestone.DoesNotExist, Milestone.MultipleObjectsReturned) as e:
        target_completion = None

    return render(request, 'projects/meta.html', {
        'project': project,
        'target_completion': target_completion,
    })



@permission_required('projects.can_view_all', raise_exception=True)
def detail(request, project_id):
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
   
    
    todo_list = ToDo.objects.prefetch_related('tickets')
    todos=todo_list.filter(project=project, due_on=project.current_sprint_end)


    # paginate on tickets queryset
    do_pagination = False
    if not request.GET.get('showall', False):
        paginator = Paginator(tickets, TICKETS_PAGINATE_BY)
        page = request.GET.get('page')

        try:
            tickets = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            tickets = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            tickets = paginator.page(paginator.num_pages)
        finally:
            do_pagination = True

    components = project.components()
    work = project.latestWork(10)
    milestones = Milestone.objects.filter(project=project)
        
    return render(request, "projects/detail.html", {
        'project': project,
        'tickets': tickets,
        'queries': connection.queries,
        'components': components,
        'work': work,
        'milestones': milestones,
        'filterset': ticket_filterset,
        "do_pagination": do_pagination,
        'page': tickets,
        'todos': todos,
    })

@permission_required('projects.change_project')
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

@permission_required('projects.add_project')
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

@permission_required('projects.can_view_all', raise_exception=True)
def search(request, project_id):
    project = get_object_or_404(Project,pk= project_id)
    q = request.GET.get('contains', '')
    tickets = Ticket.objects.filter(project=project).filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q))
    todos = ToDo.objects.filter(project=project).filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q))
    tickets = match_results(q, tickets)
    todos = match_results(q, todos)
    results = tickets.count() + todos.count()
    
    return render(request, 'projects/search-results.html', {
        'tickets': tickets,
        'todos': todos,
        'project': project,
        'results': results,
    })


@permission_required('projects.change_project')
def edit_sprint(request, project_id):
    project = get_object_or_404(Project,pk= project_id)
    if request.method == "POST":
        form = ProjectSprintForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
    else:
        form = ProjectSprintForm(instance=project)
    return render(request, 'projects/edit_sprint.html', {
        'form': form,})

def match_results(q, tickets):
    for ticket in tickets:
        match = re.search(q, ticket.body, re.IGNORECASE) 
        if match is not None:
            start = match.start() - 20 if (match.start() -20) > 0 else match.start() 
            end = match.end() + 20 if (match.end() + 20 is not None) else match.end() 
            repl = '<strong>%s</strong>' % match.group()
            pat = re.compile(q, re.I)
            body = pat.sub(repl, ticket.body, 1)
            ticket.match = body[start:end+20]
        match = re.search(q, ticket.title, re.IGNORECASE )
        if match is not None:    
            start = match.start() - 20 if (match.start() -20) > 0 else match.start() 
            end = match.end() + 20 if (match.end() + 20 is not None) else match.end() 
            repl = '<strong>%s</strong>' % match.group()
            pat = re.compile(q, re.I)
            title = pat.sub(repl, ticket.title, 1)
            ticket.match = title[start:end+20]
    return tickets
