from datetime import datetime, timedelta
from django import forms
from .models import Ticket, Comment, Work, TicketStatus, TicketPriority, WorkType
from ..projects.models import Component

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        project = kwargs.pop("project")
        created_by = kwargs.pop("created_by")

        super(TicketForm, self).__init__(*args, **kwargs)

        # set the foreign key fields specified by the caller
        self.instance.project = project
        self.instance.created_by = created_by

        # remove the blank choices from the fields
        self.fields['status'].empty_label = None
        self.fields['priority'].empty_label = None
        self.fields['component'].empty_label = None

        if not self.is_bound:
            self.fields['status'].initial = TicketStatus.objects.get(is_default=1)
            self.fields['priority'].initial = TicketPriority.objects.get(is_default=1)
            self.fields['component'].initial = project.defaultComponent()
            self.fields['estimated_time'].initial = "1:00"
            self.fields['assigned_to'].initial = created_by

        # a ticket doesn't neccessarily need to be assigned to anyone.
        # for some reason, you can't set this in the model field
        self.fields['assigned_to'].required = False
        self.fields['component'].required = False
        # the QuickTicketForm inherits from this class, but exlcudes the title field,
        # hence the if statement here
        if "title" in self.fields:
            self.fields['title'].required = False

        self.fields['body'].required = False

        # only display components associated with this project
        self.fields['component'].queryset = Component.objects.filter(project=project)

    def clean(self):
        cleaned_data = super(TicketForm, self).clean()

        # infer the title based on the body, if the title is not set
        body = cleaned_data.get("body", None)
        title = cleaned_data.get("title", None)

        if body and not title:
            # keep the title fairly short  
            max_length = min(Ticket._meta.get_field('title').max_length, 80)
            if len(body) > max_length:
                last_space = body.rfind(' ', 0, max_length)
                cleaned_data['title'] = body[0:last_space]
            else:
                cleaned_data['title'] = body
        elif title and not body:
            cleaned_data['body'] = title
        elif not title and not body:
            self._errors['body'] = self.error_class(['This field is required'])

        return cleaned_data

    class Meta:
        model = Ticket
        exclude = ('project', 'created_by')
        widgets = {'body': forms.Textarea(attrs={'cols': 100})}

class QuickTicketForm(TicketForm):
    add_work = forms.BooleanField(required=False)
    TIME_CHOICES = (
        ('00:30', '30m'),
        ('01:00', '1h'),
        ('01:30', '1h 30m'),
        ('02:00', '2h'),
        ('02:30', '2h 30m'),
        ('03:00', '3h'),
        ('03:30', '3h 30m'),
        ('04:00', '4h'),
        ('04:30', '4h 30m'),
        ('05:00', '5h'),
        ('05:30', '5h 30m'),
        ('06:00', '6h'),
        ('06:30', '6h 30m'),
        ('07:00', '7h'),
        ('07:30', '7h 30m'),
        ('08:00', '8h'),
    )
    estimated_time = forms.ChoiceField(choices=TIME_CHOICES)

    def __init__(self, *args, **kwargs):
        super(QuickTicketForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(QuickTicketForm, self).save(*args, **kwargs)
        # add the work line item too
        if self.cleaned_data.get('add_work', False):
            w = Work()
            w.description = "Did stuff"
            w.time = self.instance.estimated_time
            w.type = WorkType.objects.default()
            w.ticket = self.instance
            w.created_by = self.instance.created_by
            # assume the work started w.time hours/minutes ago
            w.started_on = datetime.now() - timedelta(hours=w.time.hour, minutes=w.time.minute)
            w.save()

    class Meta:
        model = Ticket
        exclude = ('project', 'created_by', 'started_on')
        widgets = {'body': forms.Textarea(attrs={'cols': 30})}

class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        created_by = kwargs.pop("created_by")
        ticket = kwargs.pop("ticket")

        super(CommentForm, self).__init__(*args, **kwargs)

        # set the foreign key fields specified by the caller
        self.instance.ticket = ticket
        self.instance.created_by = created_by

    class Meta:
        model = Comment
        exclude = ('ticket', 'created_by')

class WorkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        ticket = kwargs.pop("ticket")
        created_by = kwargs.pop("created_by")

        super(WorkForm, self).__init__(*args, **kwargs)

        self.instance.ticket = ticket
        self.instance.created_by = created_by

        self.fields['type'].empty_label = None
        self.fields['started_on'].required = False

        if not self.is_bound:
            self.fields['type'].initial = WorkType.objects.get(is_default=1)
            self.fields['started_on'].initial = datetime.now()

    def clean_started_on(self):
        started_on = self.cleaned_data.get('started_on', "")
        if not started_on:
            started_on = datetime.now()

        return started_on

    class Meta:
        model = Work
        exclude = ('ticket', 'created_by')
        widgets = {"description": forms.TextInput(attrs={"placeholder": "description"})}

