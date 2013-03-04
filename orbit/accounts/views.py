from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from ..tickets.models import Ticket, Work
from orbit.utils import querySetToJSON

@login_required
def profile(request):
    user = request.user
    # grab all the tickets created_by or assigned to this user
    tickets = Ticket.objects.tickets().filter(Q(created_by=user) | Q(assigned_to=user))
    # get all the work created by this user, but isn't yet done
    running_work = Work.objects.filter(created_by=user).exclude(state=Work.DONE).select_related("created_by", "type", "ticket").order_by('-created_on')
    tickets_json = querySetToJSON(tickets)

    return render(request, "accounts/profile.html", {
        "tickets": tickets,
        "running_work": running_work,
        "queries": connection.queries,
        "tickets_json": tickets_json,
    })
