from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from ..forms import MilestoneForm
from ..models import Project, Milestone


@permission_required('projects.add_milestone')
def create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = MilestoneForm(request.POST, project=project, created_by=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("projects-detail", args=(project.pk,)))
    else:
        form = MilestoneForm(project=project, created_by=request.user)

    return render(request, 'projects/milestones/create.html', {
        'project': project,
        'form': form,
    })


@permission_required('projects.can_view_all', raise_exception=True)
def detail(request, milestone_id):
    milestone = get_object_or_404(Milestone, pk=milestone_id)
    return render(request, 'projects/milestones/detail.html', {
        'project': milestone.project,
        'milestone': milestone,
    })


@permission_required('projects.change_milestone')
def edit(request, milestone_id):
    milestone = get_object_or_404(Milestone, pk=milestone_id)
    project = milestone.project
    if request.method == "POST":
        form = MilestoneForm(
            request.POST, instance=milestone, project=project, created_by=milestone.created_by)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('milestones-detail', args=(project.pk,)))
    else:
        form = MilestoneForm(instance=milestone, project=project, created_by=milestone.created_by)

    return render(request, 'projects/milestones/create.html', {
        'project': project,
        'form': form,
    })
