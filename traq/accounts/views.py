from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q

from traq.utils import querySetToJSON
from traq.permissions import STAFF_GROUP, CLIENT_GROUP
from traq.projects.models import Project

from ..tickets.models import Ticket, Work, TicketStatus
from ..tickets.constants import TICKETS_PAGINATE_BY
from ..tickets.filters import TicketFilterSet
from ..projects.views.reports import _intervalHelper
from ..projects.forms import ReportIntervalForm


@login_required
def profile(request, tickets=''):
    user = request.user
    if user.groups.filter(name='arc'):
        return _tickets(request, tickets)
    elif user.groups.filter(name=CLIENT_GROUP):
        return _projects(request)
    else:
        return _invoices(request)

def _tickets(request, tickets=''):
    user = request.user
    # grab all the tickets created_by or assigned to this user
    if(tickets == 'created_by'):
        tickets = Ticket.objects.tickets().filter(Q(created_by=user))
    elif(tickets =='assigned'):
        tickets = Ticket.objects.tickets().filter(Q(assigned_to=user))
    else:    
        tickets = Ticket.objects.tickets().filter(Q(created_by=user) | Q(assigned_to=user))

    ticket_filterset = TicketFilterSet(request.GET, queryset=tickets)
    q = request.GET.get('contains', '')
    if request.GET.get('due_on') == 'a':
        tickets = ticket_filterset.qs.order_by("-due_on")
    elif request.GET.get('due_on') == 'd':
        tickets = ticket_filterset.qs.order_by("due_on")
    elif request.GET.get('contains'):
        tickets = ticket_filterset.qs.filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q))
    else:
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

    # get all the work created by this user, but isn't yet done
    running_work = Work.objects.filter(created_by=user).exclude(state=Work.DONE).select_related("created_by", "type", "ticket").order_by('-created_on')

    return render(request, "accounts/tickets.html", {
        "tickets": tickets,
        "running_work": running_work,
        "queries": connection.queries,
        "do_pagination": do_pagination,
        "page": tickets,
        'filterset': ticket_filterset,
    })

def _invoices(request):
    user = request.user
    projects = Project.objects.all()

    return render(request, "accounts/invoices.html", {
        "projects": projects,
    })

def _projects(request):
    user = request.user
    if user.groups.filter(name=STAFF_GROUP):
	projects = Project.objects.all()
    else:
	projects = Project.objects.filter(clients=request.user)
    return render(request, "accounts/projects.html", {
        "projects": projects,
    })

@login_required
def timesheet(request):
    user = request.user
    tickets = Ticket.objects.tickets().filter(Q(assigned_to=user))
    form, interval = _intervalHelper(request)

    print form

    return render(request, "accounts/timesheet.html", {
        'tickets': tickets,
        'form': form,
        'interval': interval })

def _miniIntervalHelper(request):
    interval = ()
    
    if request.GET.get('submit'):
        form = ReportIntervalForm(request.GET)
        if form.is_valid():
            interval = (form.cleaned_data['start'], form.cleaned_data['end'])
    if interval == ():
        now = datetime.utcnow().replace(tzinfo=utc)
        earlier = now - timedelta(days=30)
        interval = (earlier.date(), now.date())

        if not request.GET.get('submit'):
            form = ReportIntervalForm(initial={"start": interval[0], "end": interval[1]})

    interval = (interval[0], datetime.combine(interval[1], time(hour=23, minute=59, second=59)))
    return form, interval