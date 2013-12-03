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
from traq.todos.models import ToDo

# there's an annoying circular dependency between the ticket and project apps 
# so this import needs to be after project models are imported
from traq.tickets.filters import TicketFilterSet
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User



@permission_required('projects.can_view_all', raise_exception=True)
def all(request):
    projects = []
    projects.append(Project.objects.filter(status=Project.ACTIVE))
    projects.append(Project.objects.filter(status=Project.INACTIVE))
    return render(request, 'projects/all.html', {
        'projects': projects,
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
    
    if project.is_scrum:
        tickets =tickets.filter(due_on=project.current_sprint_end)
        template = 'projects/scrum_detail.html'
    else:
        template = 'projects/detail.html'
    todos = ToDo.objects.prefetch_related('tickets')
    todos=todos.filter(project=project, due_on=project.current_sprint_end)
    print todos
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
    sess_sprint = "sprint_end%d" % project.pk
    sprint_end = request.session.get(sess_sprint, project.current_sprint_end)
    next = sprint_end + timedelta(days=14)
    prev = sprint_end - timedelta(days=14)
    
    return render(request, template, {
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
        'sprint_end': sprint_end,
        'next': next,
        'prev':prev,
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

def which_sprint(request, project_id):
    project = get_object_or_404(Project,pk= project_id)
    if request.method == "POST":
        end = request.POST.get('current_sprint_end', project.current_sprint_end)
        sprint = "sprint_end%d" % project.pk
        request.session[sprint] = datetime.strptime(end, "%Y-%m-%d").date()
    return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
