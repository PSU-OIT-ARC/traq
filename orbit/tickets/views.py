from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from .forms import TicketForm, CommentForm
from .models import Ticket, Comment
from ..projects.models import Project

def detail(request, project_id, ticket_id):
    project = get_object_or_404(Project, pk=project_id)
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    comments = Comment.objects.filter(ticket=ticket)

    if request.POST:
        comment_form = CommentForm(request.POST, created_by=request.user, ticket=ticket)
        if comment_form.is_valid():
            comment_form.save()
            return HttpResponseRedirect(request.path)
    else:
        comment_form = CommentForm(created_by=request.user, ticket=ticket)

    return render(request, 'tickets/detail.html', {
        'project': project,
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
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
    })

def edit(request, project_id, ticket_id):
    project = get_object_or_404(Project, pk=project_id)
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket, project=project, created_by=ticket.created_by)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("tickets-detail", args=(project.pk, form.instance.pk)))
    else:
        form = TicketForm(instance=ticket, project=project, created_by=ticket.created_by)

    return render(request, 'tickets/create.html', {
        'form': form,
    })
