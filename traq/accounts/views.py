from datetime import datetime, date, timedelta, time

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from django.utils.timezone import utc, make_aware, get_current_timezone

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
    """
    Redirect user to correct view based
    on their group.
    """
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
    form, interval, date_list = _miniIntervalHelper(request)
    work_by_date = []

    #print "Timesheet: %s | %s" % (interval[0], interval[1])

    work = Work.objects.filter(ticket__assigned_to=user, \
            state=Work.DONE, \
            ticket__is_deleted=False, \
            started_on__gte=interval[0], \
            done_on__lte=interval[1] 
            ).order_by('started_on')

    work_by_date = dict([(d.date(), []) for d in date_list])

    total_hours = timedelta(0)
    
    for w in work:
        work_by_date[w.started_on.date()].append(w)
        total_hours += timedelta(hours=w.time.hour,minutes=w.time.minute,seconds=w.time.second)

    return render(request, "accounts/timesheet.html", {
        'tickets': tickets,
        'form': form,
        'interval': interval,
        'work': work,
        'date_list': date_list,
        'work_by_date': sorted(work_by_date.items()),
        'total_hours': total_hours,
         })

def _miniIntervalHelper(request):
    interval = ()
    date_list = []
    actual_td = 0
    
    if request.GET.get('submit'):

        form = ReportIntervalForm(request.GET)
        if form.is_valid():
            interval = (form.cleaned_data['start'], form.cleaned_data['end'])
            # intervals will be datetime.date type. MUST convert to datetime.datetime type
            now = datetime(interval[1].year, interval[1].month, interval[1].day)

    if interval == ():        
        # default timesheet period: 16th of current month to the 15th of next month
        # NOTE/TODO: may make date range change depending where you are in the month.
        # i.e. seeing current-future timesheet vs. past-current timesheet
        now = datetime(date.today().year, date.today().month, 15)
        now = now.replace(hour=0, minute=0)
        delta = now - timedelta(days=30)
        earlier = datetime(delta.year, delta.month, 16)
        earlier = earlier.replace(hour=0, minute=0)
        interval = (earlier.date(), now.date())

        if not request.GET.get('submit'):
            form = ReportIntervalForm(initial={"start": interval[0], "end": interval[1]})

    # we need to convert the date and datetime objects into aware datetime objects
    interval = (make_aware(datetime.combine(interval[0], time()), get_current_timezone()),
                make_aware(datetime.combine(interval[1], time()), get_current_timezone()))
    now = make_aware(now, get_current_timezone())
    _td = interval[1] - interval[0]
    actual_td = _td.days + 1
    date_list = [now - timedelta(days=x) for x in range(0, actual_td)]

    return form, interval, date_list
