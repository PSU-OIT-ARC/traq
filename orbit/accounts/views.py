from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from ..tickets.models import Ticket, Work, TicketStatus
from orbit.utils import querySetToJSON
from orbit.permissions.checkers import STAFF_GROUP
from orbit.projects.models import Project

@login_required
def profile(request):
    user = request.user
    if user.groups.filter(name=STAFF_GROUP):
        return _tickets(request)
    else:
        return _invoices(request)

def _tickets(request):
    user = request.user
    # grab all the tickets created_by or assigned to this user
    tickets = Ticket.objects.tickets().filter(Q(created_by=user) | Q(assigned_to=user)).exclude(status=TicketStatus.objects.closed())
    # get all the work created by this user, but isn't yet done
    running_work = Work.objects.filter(created_by=user).exclude(state=Work.DONE).select_related("created_by", "type", "ticket").order_by('-created_on')
    tickets_json = querySetToJSON(tickets)

    return render(request, "accounts/tickets.html", {
        "tickets": tickets,
        "running_work": running_work,
        "queries": connection.queries,
        "tickets_json": tickets_json,
    })

def _invoices(request):
    user = request.user
    projects = Project.objects.all()

    return render(request, "accounts/invoices.html", {
        "projects": projects,
    })
