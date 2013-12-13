import os
import uuid
from datetime import datetime, timedelta
from django.conf import settings as SETTINGS
from django import forms
from django.contrib.auth.models import User
from .models import (
    Ticket, 
    Comment, 
    Work, 
    TicketStatus, 
    TicketPriority, 
    WorkType, 
    TicketFile,
)
from ..projects.models import Component, Milestone

class TicketForm(forms.ModelForm):
    """Ticket creation and editing form"""
    # these are fields that aren't part of the Ticket model, so they need to be
    # added here 
    add_work = forms.BooleanField(required=False)
    files = forms.FileField(required=False, widget=forms.FileInput(attrs={"multiple": True}))
    existing_files = forms.ModelMultipleChoiceField(required=False, queryset=None, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        project = kwargs.pop("project")
        # keep this is an instance var since we need it in save()
        self.user = kwargs.pop("user")
        self.todos = kwargs.pop('todo', None)
        super(TicketForm, self).__init__(*args, **kwargs)

        # if this is a new ticket, we need to set some additional fields
        if self.instance.pk is None:
            self.instance.created_by = self.user
            self.instance.project = project
        
        if project.is_scrum:
            self.fields['due_on'].initial = project.current_sprint_end 
        # remove the blank choices from the fields
        self.fields['status'].empty_label = None
        self.fields['priority'].empty_label = None
        self.fields['component'].empty_label = None

        # set some sensible default values
        if not self.is_bound:
            self.fields['status'].initial = TicketStatus.objects.get(is_default=1)
            self.fields['priority'].initial = TicketPriority.objects.get(is_default=1)
            self.fields['component'].initial = project.defaultComponent()
            self.fields['estimated_time'].initial = "1:00"
            self.fields['assigned_to'].initial = self.user

        if self.todos:
            self.fields['body'].initial = "from todo: \n%s " % self.todos.body

        # one of these fields will be required, but we handle that in the clean
        # method
        self.fields['title'].required = False
        self.fields['body'].required = False

        # only display components and milestones associated with this project
        self.fields['component'].queryset = Component.objects.filter(project=project)
        self.fields['milestone'].queryset = Milestone.objects.filter(project=project)
        self.fields['existing_files'].queryset = TicketFile.objects.filter(ticket=self.instance)

    def hasFiles(self):
        # does this Ticket have any files associated with it?
        return self.fields['existing_files'].queryset.count() != 0

    def clean(self):
        cleaned_data = super(TicketForm, self).clean()

        # infer the title based on the body, if the title is not set, or vis-a-vera
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

    def save(self, *args, **kwargs):
        super(TicketForm, self).save(*args, **kwargs)
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
            w.done_on = datetime.now()
            w.state = Work.DONE
            w.save()

        # remove any files
        for tf in self.cleaned_data.get('existing_files', []):
            tf.delete()

        # add any files
        if self.files:
            files = self.files.getlist("files")
            for f in files:
                tf = TicketFile(ticket=self.instance, file=f, uploaded_by=self.user)
                tf.save()

    class Meta:
        model = Ticket
        fields = (
            'title', 
            'body', 
            'started_on', 
            'estimated_time', 
            'is_deleted',
            'is_extra', 
            'is_internal',
            'assigned_to', 
            'status', 
            'priority', 
            'component',
            'milestone',
            'due_on',
            'release',
            'branch',
            
        )

        widgets = {
            "release": forms.TextInput(attrs={"placeholder": "release"}),
            "branch": forms.TextInput(attrs={"placeholder": "branch"}),
            "due_on": forms.DateTimeInput(attrs={'type':'date'})
        }

class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        created_by = kwargs.pop("created_by")
        
        ticket = kwargs.pop("ticket", None)
        
        todo = kwargs.pop('todo', None)
        super(CommentForm, self).__init__(*args, **kwargs)

        # set the foreign key fields specified by the caller
        self.instance.created_by = created_by
        self.instance.todo = todo
        self.instance.ticket = ticket

    class Meta:
        model = Comment
        fields = (
            'body',
            'is_deleted',
            )

class WorkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        ticket = kwargs.pop("ticket")
        user = kwargs.pop("user")

        super(WorkForm, self).__init__(*args, **kwargs)

        # set the foreign key fields specified by the caller, but only if this
        # is a new object
        if self.instance.pk is None:
            self.instance.ticket = ticket
            self.instance.created_by = user

        # get rid of the stupid ----- option on the drop downs
        self.fields['type'].empty_label = None
        self.fields['started_on'].required = False

        if not self.is_bound:
            # set some nice default values
            self.fields['type'].initial = WorkType.objects.get(is_default=1)
            self.fields['started_on'].initial = datetime.now()

    def clean_started_on(self):
        # if this field is empty, assume the work started now
        started_on = self.cleaned_data.get('started_on', "")
        if not started_on:
            started_on = datetime.now()

        return started_on

    class Meta:
        model = Work
        fields = (
            'description',
            'billable',
            'time',
            'started_on',
            'type',
            'is_deleted',
        )
        # some fancy HTML5 placeholder text
        widgets = {"description": forms.TextInput(attrs={"placeholder": "description"})}

class BulkForm(forms.Form):
    priority = forms.ModelChoiceField(queryset=TicketPriority.objects.all(), required=False, empty_label=None)
    status = forms.ModelChoiceField(queryset=TicketStatus.objects.all(), required=False, empty_label=None)
    due_on = forms.DateTimeField(required=False)
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all().order_by("username"), required=False)
    # the queryset will get reset in __init__
    component = forms.ModelChoiceField(queryset=Component.objects.all(), required=False, empty_label=None)
    milestone = forms.ModelChoiceField(queryset=Milestone.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project")

        super(BulkForm, self).__init__(*args, **kwargs)

        # base the queryset on the project
        self.fields['component'].queryset = Component.objects.filter(project=project)
        self.fields['milestone'].queryset = Milestone.objects.filter(project=project)

        # every field needs a checkbox that says if the field should be updated
        new_fields = {}
        for name, field in self.fields.items():
            new_fields[name + "_update"] = forms.BooleanField(required=False)
            # add a function to the field that allows easy access to the
            # corresponding update checkbox in a template
            self.fields[name].update_field = lambda name=name: self[name + "_update"]
        self.fields.update(new_fields)

    def editableFields(self):
        # return the list of fields that should be display on the template
        keys = ['priority', 'status', 'due_on', 'component', 'milestone', 'assigned_to']
        return [self[k] for k in keys]

    def clean(self):
        cleaned = super(BulkForm, self).clean()
        # for each *_update field, check to see if it is checked
        # if it is, make sure the corresponding field has a good value
        # if it doesn't add an error
        for k, field in self.fields.items():
            if k.endswith("_update"):
                is_being_updated = cleaned.get(k, None)
                corresponding_name = k[:-len("_update")]
                corresponding_data = cleaned.get(corresponding_name, None)
                # they didn't fill out the field
                if is_being_updated and corresponding_data == None:
                    # if the field has an empty value specified, then it is ok
                    empty_ok = getattr(self.fields[corresponding_name], 'empty_label', None)
                    if not empty_ok: 
                        self._errors[corresponding_name] = self.error_class(['Fail'])

        return cleaned

    def bulkUpdate(self, ticket_ids):    
        # figure out all the fields that needs to be updated on a ticket
        change_to = {}
        for k, field in self.fields.items():
            is_being_updated = self.cleaned_data.get(k, None)
            corresponding_name = k[:-len("_update")]
            corresponding_data = self.cleaned_data.get(corresponding_name, None)

            if is_being_updated:
                change_to[corresponding_name] = corresponding_data

        # for each ticket, update all the fields specified on the form
        for ticket_id in ticket_ids:
            ticket = Ticket.objects.get(pk=ticket_id)

            for k, v in change_to.items():
                setattr(ticket, k, v)

            ticket.save()

