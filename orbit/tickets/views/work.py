from datetime import datetime, time
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from ..forms import TicketForm, CommentForm, WorkForm
from ..models import Ticket, Comment, Work, WorkType
from orbit.projects.models import Project
from orbit.permissions.decorators import can_view, can_edit, can_create

@can_edit(Work)
def edit(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    ticket = work.ticket
    project = ticket.project
    if request.method == "POST":
        form = WorkForm(request.POST, instance=work, created_by=request.user, ticket=ticket)
        if form.is_valid():
            work.done()
            form.save()
            return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))
    else:
        work.time = work.duration()
        form = WorkForm(instance=work, created_by=request.user, ticket=ticket)

    return render(request, 'tickets/work_edit.html', {
        'form': form,
        'ticket': ticket,
        'project': project,
        'work': work,
    })

HAD_RUNNING_WORK_MESSAGE = """<strong>Dawg!</strong> You had other running work, which was paused for you. You're welcome."""

@can_create(Work)
def create(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    project = ticket.project

    had_running_work = Work.objects.pauseRunning(created_by=request.user)

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

@can_edit(Work)
def pause(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    ticket = work.ticket
    work.pause()
    return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))

@can_edit(Work)
def continue_(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    ticket = work.ticket
    had_running_work = Work.objects.pauseRunning(created_by=request.user)
    work.continue_()
    messages.success(request, 'Work Started')
    if had_running_work:
        messages.warning(request, HAD_RUNNING_WORK_MESSAGE)

    return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))
