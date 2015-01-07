from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from traq.tickets.forms import TicketForm, CommentForm
from traq.todos.filters import ToDoFilterSet, ToDoPriorityFilterSet
from traq.utils import get_next_scrum_day, BootstrapErrorList
from traq.tickets.constants import TICKETS_PAGINATE_BY
from traq.projects.models import Project
from traq.tickets.models import Ticket
from traq.todos.models import ToDo
from traq.todos.forms import *
from django.contrib.auth.decorators import permission_required
from traq.permissions.decorators import can_view_project, can_view_todo
import datetime

@can_view_project
@permission_required('todos.add_todo')
def listing(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    todo_filterset = ToDoFilterSet(request.GET, queryset=ToDo.objects.filter(project=project, is_deleted=False), project_id = project_id)
    todos = todo_filterset
    if project.is_scrum:
        backlog = project.current_sprint_end - datetime.timedelta(days=2)
    else: 
        backlog = None
    
    q = request.GET.get('q', '')
    if request.GET.get('q'):
        todos = todos.qs.filter(Q(body__icontains=q)|Q(title__icontains=q)|Q(pk__icontains=q))
    if not request.GET.get('showall', False):
        paginator = Paginator(todos, TICKETS_PAGINATE_BY)
        page = request.GET.get('page')

        try:
            todos = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            todos = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            todos = paginator.page(paginator.num_pages)
        finally:
            do_pagination = True

    return render(request, 'todos/list.html', {
        'todos': todos,
        'project': project,
        'backlog': backlog,
        'page':todos,
        'do_pagination': do_pagination,
        'filterset': todo_filterset,
        })

@can_view_project
@permission_required('todos.add_todo')
def create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ToDoForm(request.POST, request.FILES, user=request.user, project=project, error_class=BootstrapErrorList)
        if form.is_valid():
            form.save()
            todo = form.instance

            messages.success(request, 'To Do Item Added')

            # save the ticket form data so the user doesn't have to reinput
            # everything again, if they want to create a similar ticket in the
            # future. Save the data on a per project basis (using the project's pk)
            if "todo_form" not in request.session:
                request.session['todo_form'] = {}
            request.session['todo_form'][project.pk] = form.cleaned_data
            # Django won't know to save the session because we are modifying a
            # 2D dictionary
            request.session.modified = True

            # Go to the ticket detail page, or if they clicked the "Save and
            # add another ticket button, display the ticket form again
            if request.POST.get("submit", "submit").lower() == "submit":
                return HttpResponseRedirect(reverse("todos-detail", args=[todo.pk,]))
                #return HttpResponseRedirect(request.path)
            else:
                return HttpResponseRedirect(request.path)
    else:
        # if the user submitted a ticket for this project recently, the form
        # data will be in their session (since we save it in the above code).
        # Use their last submission as the initial data for the form (since in
        # all likelyhood, most of the fields will be the same)
        initial_data = request.session.get("todo_form", {}).get(project.pk, {})
        # theses fields vary on every ticket, so there is no reason to include
        # them in the initial data on the form
        initial_data.pop("body", None)
        initial_data.pop("title", None)
        initial_data.pop("add_ticket", None)
        form = ToDoForm(initial=initial_data, user=request.user, project=project)
    return render(request, 'todos/create.html', {
        'form': form,
        'project': project,
    })

@can_view_todo    
@permission_required('todos.add_todo')
def detail(request, todo_id):
    todo = get_object_or_404(ToDo, pk=todo_id)
    project = todo.project
    files = TicketFile.objects.filter(todo=todo)
    comments = Comment.objects.filter(todo=todo).select_related('created_by')
    comment_form = CommentForm(created_by=request.user, todo=todo)
    if request.POST:
        # there are a few forms on the page, so we use this to determine which
        # was submitted
        form_type = request.POST['form_type']
        if form_type == "comment_form":
            comment_form = CommentForm(request.POST, created_by=request.user, todo=todo)
            if comment_form.is_valid():
                comment_form.save()
                messages.success(request, 'Comment Added')
                return HttpResponseRedirect(request.path)
    
    return_to = request.GET.get('return_to', '')
    return render(request, 'todos/detail.html', {
        'project': project,
        'todo': todo,
        'comments': comments,
        'comment_form': comment_form,
        'files': files,
        'return_to':return_to,
    })

@can_view_todo
@permission_required('todos.change_todo')
def edit(request, todo_id):
    todo = get_object_or_404(ToDo, pk=todo_id)
    return_to = request.GET.get('return_to','')
    project = todo.project
    files = TicketFile.objects.filter(todo=todo)
    if request.method == "POST":
        # cache the old info about the ticket, so we know if it got changed
        form = ToDoForm(request.POST, request.FILES, user=request.user, instance=todo, project=todo.project)
        if form.is_valid():
            form.save()
            if form.instance.is_deleted:
                messages.success(request, 'To Do Item Deleted')
                if return_to == 'prioritize':
                    return HttpResponseRedirect(reverse("todos-prioritize", args=(project.pk,)))
                else:
                    return HttpResponseRedirect(reverse("todos-list", args=(project.pk,)))
            else:
                messages.success(request, 'To Do Item Edited')
                if return_to == 'prioritize':
                    return HttpResponseRedirect('%s?return_to=prioritize' % reverse("todos-detail", args=(todo.pk,)))
                else:
                    return HttpResponseRedirect(reverse("todos-detail", args=(todo.pk, )))
    else:
        form = ToDoForm(instance=todo, user=request.user, project=todo.project)

    return render(request, 'todos/create.html', {
        'form': form,
        'project': project,
        'todo': todo,
        'files':files,
    })

"""
This function has no entry in urls, and appears to never be called

@permission_required('todos.change_todo')
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
"""

@can_view_project
@permission_required('todos.change_todo')
def prioritize(request, project_id):
    if request.method == 'POST':
        rank_list = request.POST['pk'].split(',')
        for index, pk in enumerate(rank_list):
            todo = get_object_or_404(ToDo, pk=pk)
            todo.rank = index
            todo.save()
        messages.success(request, 'To Do Items Prioritized')

    
    project = get_object_or_404(Project, pk=project_id)
    todo_filterset = ToDoPriorityFilterSet(request.GET, queryset=ToDo.objects.filter(project=project, is_deleted=False, status_id=1).order_by('rank'), project_id=project_id)
    todos = todo_filterset
    return render(request, 'todos/prioritize.html', {
        'todos': todos,
        'project': project,
        'filterset': todo_filterset,
        })

@can_view_project
@permission_required('todos.change_todo')
def bulk(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    todos_ids = request.GET['todos'].split(",")
    # TODO add permissions checking on a ticket level. 

    if request.method == "POST":
        form = BulkToDoForm(request.POST, project=project)
        if form.is_valid():
            form.bulkUpdate(todos_ids)
            return HttpResponseRedirect(reverse('todos-list', args=(project.pk,)))
    else:
        form = BulkForm(project=project)

    return render(request, 'todos/bulk.html', {
        'form': form,
        'project': project,
    })


