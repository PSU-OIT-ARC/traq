from datetime import datetime, time
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from django.db.models import Q
from ..forms import TicketForm, CommentForm, WorkForm, BulkForm
from ..models import Ticket, Comment, Work, WorkType, TicketStatus, TicketFile
from traq.projects.models import Project
from traq.todos.models import ToDo
from traq.tickets.filters import TicketFilterSet
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

@permission_required('todos.add_todo')
def detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    todos = ticket.todos.all()
    #try to redirect client to todo item if it exists. else they'll get 403
    if todos:
        todo = todos[0]
        if request.user.groups.filter(name='arcclient').exists():
            messages.success(request, 'You have insufficeient privileges to see this ticket. You have been redirected to the associated to do item')
            return HttpResponseRedirect(reverse('todos-detail', args=(todo.pk,)))
    #check for arc group (staff and students should have this)
    if not request.user.groups.filter(name='arc'):
        raise PermissionDenied("Access Denied")
    project = ticket.project
    files = TicketFile.objects.filter(ticket=ticket)
    comments = Comment.objects.filter(ticket=ticket).select_related('created_by')
    if ticket.todos.all():
        comments = list(comments) + list(Comment.objects.filter(todo__pk__in=ticket.todos.all()).select_related('created_by'))
        comments.sort(key=lambda x: x.created_on)
    work = Work.objects.filter(ticket=ticket).filter(state=Work.DONE).select_related("created_by", "type").order_by('-created_on')
    running_work = Work.objects.filter(ticket=ticket).exclude(state=Work.DONE).select_related("created_by", "type").order_by('-created_on')
    times = ticket.totalTimes()
    
    return_to = request.GET.get('return_to', None)

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
        'return_to': return_to,
    })

HAD_RUNNING_WORK_MESSAGE = 'There was running work on this ticket. The work was marked as "Done".'

@permission_required('tickets.add_ticket')
def create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if "todo_id" in request.GET:
        todo = get_object_or_404(ToDo, pk=request.GET['todo_id'])
    else: 
        todo = None
    
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES, user=request.user, project=project, todo=todo)
        if form.is_valid():
            form.save()
            ticket = form.instance
            if todo:
                ticket.todos.add(todo)
                ticket.save()
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
                if "return_to" in request.GET:
                    return HttpResponseRedirect("%s?todo_id=%d&return_to=prioritize" % (reverse("tickets-detail", args=(form.instance.pk,)),todo.pk ) )
                else:
                    return HttpResponseRedirect(reverse("tickets-detail", args=(form.instance.pk,)))
            elif "todo_id" in request.GET:
                return HttpResponseRedirect("%s?todo_id=%d" % (request.path,todo.pk))
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
        form = TicketForm(initial=initial_data, user=request.user, project=project, todo=todo)

    return render(request, 'tickets/create.html', {
        'form': form,
        'project': project,
        'todo':todo,
    })

@permission_required('tickets.change_ticket')
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

@permission_required('tickets.change_ticket')
def edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    project = ticket.project
    if request.method == "POST":
        # cache the old info about the ticket, so we know if it got changed
        form = TicketForm(request.POST, request.FILES, user=request.user, instance=ticket, project=ticket.project)
        if form.is_valid():
            form.save()
            if form.instance.is_deleted:
                messages.success(request, 'Ticket Deleted')
                return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
            else:
                messages.success(request, 'Ticket Edited')
                return HttpResponseRedirect(reverse("tickets-detail", args=(form.instance.pk,)))
    else:
        form = TicketForm(instance=ticket, user=request.user, project=ticket.project)

    return render(request, 'tickets/create.html', {
        'form': form,
        'project': project,
        'ticket': ticket,
    })

@permission_required('tickets.add_ticket')
def listing(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    ticket_filterset = TicketFilterSet(request.GET, queryset=project.tickets(), project_id = project_id)
    tickets= ticket_filterset.qs.order_by('-priority', 'due_on')
    
    q = request.GET.get('q', '')
    if request.GET.get('q'):
        tickets = tickets.filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q))

    return render(request, 'tickets/list.html', {
        'tickets': tickets,
        'project': project,
        'filterset':ticket_filterset,})


@permission_required('tickets.change_comment')
def comments_edit(request, comment_id):
    # there is no corresponding comments_create view since a comment is created
    # on the ticket detail view.
    return_to = request.GET.get('return_to',None)
    comment = get_object_or_404(Comment, pk=comment_id)
    ticket = comment.ticket
    todo = comment.todo
    if ticket: 
        project = ticket.project 
    else:
        project = todo.project

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment, created_by=request.user, ticket=ticket, todo=todo)
        if form.is_valid():
            form.save()
            if ticket:
                return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))
            elif return_to:
                return HttpResponseRedirect(reverse('tickets-detail', args=(return_to,)))
            else:
                return HttpResponseRedirect(reverse('todos-detail', args=(todo.pk,)))
    else:
        form = CommentForm(instance=comment, created_by=request.user, ticket=ticket)

    object = ticket or todo
    return render(request, 'tickets/comments_edit.html', {
        'form': form,
        'comment': comment,
        'ticket': object,
        'project': project,
    })

