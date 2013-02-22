from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from .forms import TicketForm, CommentForm, WorkForm
from .models import Ticket, Comment, Work
from ..projects.models import Project, Attribute, AttributeTypeName

def detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    project = ticket.project
    comments = Comment.objects.filter(ticket=ticket)
    work = Work.objects.filter(ticket=ticket).order_by('-created_on')
    times = ticket.totalTimes()

    comment_form = CommentForm(created_by=request.user, ticket=ticket)
    work_form = WorkForm(initial={"time": "00:30:00", "description": "description"}, created_by=request.user, ticket=ticket)

    if request.POST:
        # there are a few forms on the page, so we use this to determine which
        # was submitted
        form_type = request.POST['form_type']
        if form_type == "comment_form":
            comment_form = CommentForm(request.POST, created_by=request.user, ticket=ticket)
            if comment_form.is_valid():
                comment_form.save()
                return HttpResponseRedirect(request.path)
        elif form_type == "work_form":
            work_form = WorkForm(request.POST, created_by=request.user, ticket=ticket)
            if work_form.is_valid():
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
    })
    

def create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = TicketForm(request.POST, project=project, created_by=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("tickets-detail", args=(project.pk, form.instance.pk)))
    else:
        form = TicketForm(project=project, created_by=request.user)

    return render(request, 'tickets/create.html', {
        'form': form,
        'project': project,
    })

def edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    project = ticket.project
    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket, project=project, created_by=ticket.created_by)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("tickets-detail", args=(project.pk, form.instance.pk)))
    else:
        form = TicketForm(instance=ticket, project=project, created_by=ticket.created_by)

    return render(request, 'tickets/create.html', {
        'form': form,
        'project': project,
        'ticket': ticket,
    })

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

def work_edit(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    ticket = work.ticket
    project = ticket.project
    if request.method == "POST":
        form = WorkForm(request.POST, instance=work, created_by=request.user, ticket=ticket)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('tickets-detail', args=(ticket.pk,)))
    else:
        form = WorkForm(instance=work, created_by=request.user, ticket=ticket)

    return render(request, 'tickets/work_edit.html', {
        'form': form,
        'ticket': ticket,
        'project': project,
        'work': work,
    })

