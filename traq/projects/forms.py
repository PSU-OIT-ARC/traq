import datetime
from django import forms
from .models import Project, Component, Milestone
from ..tickets.models import Ticket

class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        created_by = kwargs.pop('created_by')
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.instance.created_by = created_by

        if self.instance.pk is None:
            self.fields['target_completion_date'] = forms.DateTimeField(initial=datetime.datetime.now()+datetime.timedelta(days=180))

    def save(self, *args, **kwargs):
        is_new = self.instance.pk is None
        super(ProjectForm, self).save(*args, **kwargs)
        # add a new completion milestone to the newly created project
        if is_new:
            Milestone(
                name="Target Completion Date", 
                due_on=self.cleaned_data['target_completion_date'],
                created_by=self.instance.created_by,
                project=self.instance,
            ).save()

    class Meta:
        model = Project
        fields = (
            'name',
            'description',
            'point_of_contact',
            'invoice_description',
            'technical',
            'catch_all',
            'status',
            'is_deleted',
            'pm_email',
            'pm',
            'estimated_hours',
        )

class ComponentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        created_by = kwargs.pop('created_by')
        super(ComponentForm, self).__init__(*args, **kwargs)
        self.instance.project = project
        self.instance.created_by = created_by

        if not self.is_bound:
            # figure out the rank for this new component
            try:
                rank = Component.objects.filter(project=project).order_by('-rank')[0].rank + 1
            except IndexError:
                rank = 1
            self.fields['rank'].initial = rank

    def clean_is_deleted(self):
        # if this is an existing component, don't allow it to be deleted if
        # there are tickets in it
        is_deleted = self.cleaned_data['is_deleted']
        if is_deleted and self.instance.pk:
            count = Ticket.objects.filter(project=self.instance.project, component=self.instance).count()
            if count != 0:
                raise forms.ValidationError("You cannot delete a component with tickets still in it")
        return is_deleted

    class Meta:
        model = Component
        fields = (
            'name',
            'description',
            'invoice_description',
            'rank',
            'is_default',
            'is_deleted',
        )

class MilestoneForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        created_by = kwargs.pop('created_by')
        super(MilestoneForm, self).__init__(*args, **kwargs)
        self.instance.project = project
        self.instance.created_by = created_by

    class Meta:
        model = Milestone
        fields = (
            'name',
            'due_on',
            'is_deleted',
        )

class ReportIntervalForm(forms.Form):
    """Simple little form to select a datetime range"""
    start = forms.DateField(widget=forms.widgets.DateInput(attrs={"type": "date"}))
    end = forms.DateField(widget=forms.widgets.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned = super(ReportIntervalForm, self).clean()
        end = cleaned.get('end', None)
        start = cleaned.get('start', None)
        if start and end:
            if end < start:
                raise forms.ValidationError("The start must be less than the end")
        return cleaned
