from datetime import datetime, time
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from ..forms import TicketForm, CommentForm, WorkForm
from ..models import Ticket, Comment, Work, WorkType
from traq.projects.models import Project
from django.contrib.auth.decorators import permission_required

@permission_required('tickets.change_work')
def edit(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    ticket = work.ticket
    project = ticket.project
    if request.method == "POST":
        form = WorkForm(request.POST, instance=work, user=request.user, ticket=ticket)
        if form.is_valid():
            work.done()
            form.save()
            return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))
    else:
        # dynamically set how much time has been spent on this work item
        work.time = work.duration()
        form = WorkForm(instance=work, user=request.user, ticket=ticket)

    return render(request, 'tickets/work_edit.html', {
        'form': form,
        'ticket': ticket,
        'project': project,
        'work': work,
    })

HAD_RUNNING_WORK_MESSAGE = """<strong>Dawg!</strong> You had other running work, which was paused for you. You're welcome."""

@permission_required('tickets.add_work')
def create(request, ticket_id):
    # this is called when a user starts working on a ticket. There is another
    # work create form that is handled on the ticket detail view
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    project = ticket.project

    # since we are adding a new work item, we need to pause whatever work the
    # user was working on before (they can't work on two things at once)
    had_running_work = Work.objects.pauseRunning(created_by=request.user)

    # create a new work object with sensible defaults
    w = Work(
        ticket=ticket, 
        description="", 
        billable=True, 
        time=time(), 
        started_on=datetime.now(),
        state=Work.RUNNING,
        type=WorkType.objects.default(),
        created_by=request.user,
    )
    w.save()
    messages.success(request, 'Work Started')

    if had_running_work:
        messages.warning(request, HAD_RUNNING_WORK_MESSAGE)

    return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))

@permission_required('tickets.change_work')
def pause(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    ticket = work.ticket
    work.pause()
    return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))

@permission_required('tickets.change_work')
def continue_(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    ticket = work.ticket
    # since we are continuing a work item, we need to pause whatever work the
    # user was working on before (they can't work on two things at once)
    had_running_work = Work.objects.pauseRunning(created_by=request.user)
    work.continue_()
    messages.success(request, 'Work Started')
    if had_running_work:
        messages.warning(request, HAD_RUNNING_WORK_MESSAGE)

    return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))
