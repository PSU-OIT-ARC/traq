from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from ..tickets.models import Ticket, Work


@login_required
def profile(request):
    user = request.user
    # this is almost a duplicate of projects.models.Project.tickets()
    tickets = Ticket.objects.filter(Q(created_by=user) | Q(assigned_to=user)).select_related(
        'status', 
        'priority', 
        'assigned_to', 
        'created_by',
        'component',
    ).extra(select={
        # the sort order
        "global_order": "IF(ticket_status.importance = 0, ticket.created_on, 0)",
        # because the column name "name" is used in all these tables, alias
        # each name column with something else, so when converted to a dict,
        # the columns don't disappear
        "status_name": "ticket_status.name",
        "priority_name": "ticket_priority.name",
        "component_name": "component.name",
    }).order_by("-status__importance", "-global_order", "-priority__rank")

    running_work = Work.objects.filter(created_by=user).exclude(state=Work.DONE).select_related("created_by", "type", "ticket").order_by('-created_on')

    return render(request, "accounts/profile.html", {
        "tickets": tickets,
        "running_work": running_work,
        "queries": connection.queries,
    })
