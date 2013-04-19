from datetime import datetime, time
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from ..forms import TicketForm, CommentForm, WorkForm, BulkForm
from ..models import Ticket, Comment, Work, WorkType, TicketStatus, TicketFile
from traq.projects.models import Project
from traq.permissions.decorators import can_view, can_edit, can_create

@can_view(Ticket)
def detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    project = ticket.project
    files = TicketFile.objects.filter(ticket=ticket)
    comments = Comment.objects.filter(ticket=ticket).select_related('created_by')
    work = Work.objects.filter(ticket=ticket).filter(state=Work.DONE).select_related("created_by", "type").order_by('-created_on')
    running_work = Work.objects.filter(ticket=ticket).exclude(state=Work.DONE).select_related("created_by", "type").order_by('-created_on')
    times = ticket.totalTimes()

    # this view has two forms on it. We multiplex between the two using a
    # hidden form_type field on the page 
    comment_form = CommentForm(created_by=request.user, ticket=ticket)
    work_form = WorkForm(initial={"time": "00:30:00"}, user=request.user, ticket=ticket)

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
            work_form = WorkForm(request.POST, user=request.user, ticket=ticket)
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
        'running_work': running_work,
        'files': files,
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
        form = TicketForm(request.POST, request.FILES, user=request.user, project=project)
        if form.is_valid():
            form.save()
            ticket = form.instance

            ticket.sendNotification()
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

            # Go to the ticket detail page, or if they clicked the "Save and
            # add another ticket button, display the ticket form again
            if request.POST.get("submit", "submit").lower() == "submit":
                return HttpResponseRedirect(reverse("tickets-detail", args=(form.instance.pk,)))
            else:
                return HttpResponseRedirect(request.path)
    else:
        # if the user submitted a ticket for this project recently, the form
        # data will be in their session (since we save it in the above code).
        # Use their last submission as the initial data for the form (since in
        # all likelyhood, most of the fields will be the same)
        initial_data = request.session.get("ticket_form", {}).get(project.pk, {})
        # theses fields vary on every ticket, so there is no reason to include
        # them in the initial data on the form
        initial_data.pop("body", None)
        initial_data.pop("title", None)
        form = TicketForm(initial=initial_data, user=request.user, project=project)

    return render(request, 'tickets/create.html', {
        'form': form,
        'project': project,
    })

@can_edit(Project)
def bulk(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    ticket_ids = request.GET['tickets'].split(",")
    # TODO add permissions checking on a ticket level. 

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
        # cache the old info about the ticket, so we know if it got changed
        original_status = ticket.status
        original_assigned_to = ticket.assigned_to
        # cache the closed status object (since we do a couple comparisons with
        # it)
        closed_status = TicketStatus.objects.closed()
        form = TicketForm(request.POST, request.FILES, user=request.user, instance=ticket, project=ticket.project)
        if form.is_valid():
            form.save()
            if form.instance.is_deleted:
                messages.success(request, 'Ticket Deleted')
                return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
            elif original_status != closed_status and ticket.status == closed_status: 
                # if the user *just* closed this ticket, call the ticket.close()
                # method to clean up any remaining work left open on the ticket
                messages.success(request, 'Ticket Closed')
                had_running_work = ticket.close()
                if had_running_work:
                    messages.warning(request, HAD_RUNNING_WORK_MESSAGE)
                return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
            else:
                # send a notification if they were just reassigned to this ticket
                if original_assigned_to.pk != ticket.assigned_to.pk:
                    ticket.sendNotification()

                messages.success(request, 'Ticket Edited')
                return HttpResponseRedirect(reverse("tickets-detail", args=(form.instance.pk,)))
    else:
        form = TicketForm(instance=ticket, user=request.user, project=ticket.project)

    return render(request, 'tickets/create.html', {
        'form': form,
        'project': project,
        'ticket': ticket,
    })

@can_edit(Comment)
def comments_edit(request, comment_id):
    # there is no corresponding comments_create view since a comment is created
    # on the ticket detail view.
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

