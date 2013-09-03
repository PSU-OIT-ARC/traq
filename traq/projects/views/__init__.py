from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from django.core import serializers


from traq.permissions.decorators import can_do, can_view, can_edit, can_create
from traq.tickets.constants import TICKETS_PAGINATE_BY
from traq.utils import querySetToJSON

from ..forms import ProjectForm
from ..models import Project, Milestone

# there's an annoying circular dependency between the ticket and project apps 
# so this import needs to be after project models are imported
from traq.tickets.filters import TicketFilterSet


@can_do()
def all(request):
    projects = []
    projects.append(Project.objects.filter(status=Project.ACTIVE))
    projects.append(Project.objects.filter(status=Project.INACTIVE))
    return render(request, 'projects/all.html', {
        'projects': projects,
    })

@can_view(Project)
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

@can_view(Project)
def detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    ticket_filterset = TicketFilterSet(request.GET, queryset=project.tickets())
    # Hack for querySetToJSON's raw sql execution; must put datetime in quotes 
    if request.GET.get('due_on') is not None:
        gets = request.GET.copy()
        gets['due_on'] = "'%s'" % gets['due_on']
        for_json  = TicketFilterSet(gets, queryset=project.tickets())
        tickets_json = querySetToJSON(for_json.qs)
    else:
        tickets_json = querySetToJSON(ticket_filterset.qs)
    # XXX: not DRY, but there is no systemic way to request this ordering
    #      from the context of a QuerySet
    tickets = ticket_filterset.qs.order_by("-status__importance", "-global_order", "-priority__rank")

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

    return render(request, 'projects/detail.html', {
        'project': project,
        'tickets': tickets,
        'queries': connection.queries,
        'components': components,
        'work': work,
        'tickets_json': tickets_json,
        'milestones': milestones,
        'filterset': ticket_filterset,
        "do_pagination": do_pagination,
        'page': tickets,
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
