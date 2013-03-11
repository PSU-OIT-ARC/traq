from datetime import datetime, time
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from ..forms import TicketForm, CommentForm, WorkForm, BulkForm
from ..models import Ticket, Comment, Work, WorkType, TicketStatus
from orbit.projects.models import Project
from orbit.permissions.decorators import can_view, can_edit, can_create

@can_view(Ticket)
def detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    project = ticket.project
    comments = Comment.objects.filter(ticket=ticket).select_related('created_by')
    work = Work.objects.filter(ticket=ticket).filter(state=Work.DONE).select_related("created_by", "type").order_by('-created_on')
    running_work = Work.objects.filter(ticket=ticket).exclude(state=Work.DONE).select_related("created_by", "type").order_by('-created_on')
    times = ticket.totalTimes()

    # this view has two forms on it
    comment_form = CommentForm(created_by=request.user, ticket=ticket)
    work_form = WorkForm(initial={"time": "00:30:00"}, created_by=request.user, ticket=ticket)

    if request.POST:
        # there are a few forms on the page, so we use this to determine which
        # was submitted
        form_type = request.POST['form_type']
        if form_type == "comment_form":
            comment_form = CommentForm(request.POST, created_by=request.user, ticket=ticket)
            if comment_form.is_valid():
                comment_form.save()
                messages.success(request, 'Comment Added')
                return HttpResponseRedirect(request.path)
        elif form_type == "work_form":
            work_form = WorkForm(request.POST, created_by=request.user, ticket=ticket)
            if work_form.is_valid():
                messages.success(request, 'Work Added')
                work_form.instance.done()
                work_form.save()
                return HttpResponseRedirect(request.path)

    return render(request, 'tickets/detail.html', {
        'project': project,
        'ticket': ticket,
        'comments': comments,
        'work': work,
        'comment_form': comment_form,
        'work_form': work_form,
        'times': times,
        'queries': connection.queries,
        'running_work': running_work,
    })

HAD_RUNNING_WORK_MESSAGE = 'There was running work on this ticket. The work was marked as "Done".'

@can_edit(Ticket)
def close(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    project = ticket.project
    had_running_work = ticket.close()

    messages.success(request, 'Ticket Closed')
    if had_running_work:
        messages.warning(request, HAD_RUNNING_WORK_MESSAGE)

    return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
    
@can_create(Ticket)
def create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = TicketForm(request.POST, project=project, created_by=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket Added')

            # save the ticket form data so the user doesn't have to reinput
            # everything again, if they want to create a similar ticket in the
            # future. Save the data on a per project basis (using the project's pk)
            if "ticket_form" not in request.session:
                request.session['ticket_form'] = {}
            request.session['ticket_form'][project.pk] = form.cleaned_data
            # Django won't know to save the session because we are modifying a
            # 2D dictionary
            request.session.modified = True

            # if they clicked the "Save and add another ticket button, display
            # the ticket form again
            if request.POST.get("submit", "submit").lower() == "submit":
                return HttpResponseRedirect(reverse("tickets-detail", args=(form.instance.pk,)))
            else:
                return HttpResponseRedirect(request.path)
    else:
        initial_data = request.session.get("ticket_form", {}).get(project.pk, {})
        initial_data.pop("body", None)
        initial_data.pop("title", None)
        form = TicketForm(initial=initial_data, project=project, created_by=request.user)

    return render(request, 'tickets/create.html', {
        'form': form,
        'project': project,
    })

@can_edit(Project)
def bulk(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    ticket_ids = request.GET['tickets'].split(",")
    # TODO add permissions checking on a ticket level

    if request.method == "POST":
        form = BulkForm(request.POST, project=project)
        if form.is_valid():
            form.bulkUpdate(ticket_ids)
            return HttpResponseRedirect(reverse('projects-detail', args=(project.pk,)))
    else:
        form = BulkForm(project=project)

    return render(request, 'tickets/bulk.html', {
        'form': form,
        'project': project,
    })

@can_edit(Ticket)
def edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    project = ticket.project
    if request.method == "POST":
        original_status = ticket.status
        form = TicketForm(request.POST, instance=ticket, project=project, created_by=ticket.created_by)
        if form.is_valid():
            form.save()
            if not form.instance.is_deleted:
                closed_status = TicketStatus.objects.closed()
                # if the user just closed this ticket, call the ticket.close()
                # method to clean up any remaining work left open on the ticket
                if original_status != closed_status and ticket.status == closed_status:
                    messages.success(request, 'Ticket Closed')
                    had_running_work = ticket.close()
                    if had_running_work:
                        messages.warning(request, HAD_RUNNING_WORK_MESSAGE)
                    return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
                else:
                    messages.success(request, 'Ticket Editied')
                return HttpResponseRedirect(reverse("tickets-detail", args=(form.instance.pk,)))
            else:
                messages.success(request, 'Ticket Deleted')
                return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
    else:
        form = TicketForm(instance=ticket, project=project, created_by=ticket.created_by)

    return render(request, 'tickets/create.html', {
        'form': form,
        'project': project,
        'ticket': ticket,
    })

@can_edit(Comment)
def comments_edit(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    ticket = comment.ticket
    project = ticket.project

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment, created_by=request.user, ticket=ticket)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))
    else:
        form = CommentForm(instance=comment, created_by=request.user, ticket=ticket)

    return render(request, 'tickets/comments_edit.html', {
        'form': form,
        'comment': comment,
        'ticket': ticket,
        'project': project,
    })

