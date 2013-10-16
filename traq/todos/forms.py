import os
import uuid
from datetime import datetime, timedelta
from django.conf import settings as SETTINGS
from django import forms
from django.contrib.auth.models import User
from traq.tickets.models import (
    Ticket, 
    Comment, 
    Work, 
    TicketStatus, 
    TicketPriority, 
    WorkType, 
    TicketFile,
)
from ..projects.models import Component, Milestone
from traq.tickets.forms import TicketForm
from traq.todos.models import ToDo

class ToDoForm(forms.ModelForm):
    """To Do Item creation and editing form--modified from ticket form"""
    files = forms.FileField(required=False, help_text="screenshots or supplementary documents", widget=forms.FileInput(attrs={"multiple": True} ))
    existing_files = forms.ModelMultipleChoiceField(required=False, queryset=None, widget=forms.CheckboxSelectMultiple())
    existing_tickets = forms.ModelMultipleChoiceField(required=False, queryset=None, widget=forms.CheckboxSelectMultiple())
    add_ticket = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'autocomplete', 'placeholder':'autocomplete'}))

    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        project = kwargs.pop("project")
        # keep this is an instance var since we need it in save()
        self.user = kwargs.pop("user")

        super(ToDoForm, self).__init__(*args, **kwargs)

        # if this is a new to do item, we need to set some additional fields
        if self.instance.pk is None:
            self.instance.created_by = self.user
            self.instance.project = project
        
        
        # remove the blank choices from the fields
        self.fields['status'].empty_label = None
        self.fields['priority'].empty_label = None
        self.fields['component'].empty_label = None

        # set some sensible default values
        if not self.is_bound:
            self.fields['status'].initial = TicketStatus.objects.get(is_default=1)
            self.fields['component'].initial = project.defaultComponent()

        # one of these fields will be required, but we handle that in the clean
        # method
        self.fields['title'].required = False
        self.fields['body'].required = False
        self.fields['estimate'].required = False

        # only display thingies associated with this project
        self.fields['component'].queryset = Component.objects.filter(project=project)
        self.fields['existing_files'].queryset = TicketFile.objects.filter(todo=self.instance)
        self.fields['existing_tickets'].queryset = Ticket.objects.filter(todos=self.instance)
    
    def hasFiles(self):
        # does this Todo have any files associated with it?
        return self.fields['existing_files'].queryset.count() != 0

    def clean(self):
        cleaned_data = super(ToDoForm, self).clean()

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
        super(ToDoForm, self).save(*args, **kwargs)
        # remove any files
        for tf in self.cleaned_data.get('existing_files', []):
            tf.delete()

        # add any files
        if self.files:
            files = self.files.getlist("files")
            for f in files:
                tf = TicketFile(todo=self.instance, file=f, uploaded_by=self.user)
                tf.save()
        
        #remove tickets 
        for todo_ticket in self.cleaned_data.get('existing_tickets', []):
            self.instance.tickets.remove(todo_ticket)

        #add existingticket
        pk = self.cleaned_data.get('add_ticket', None) 
        if pk:
            ticket = Ticket.objects.get(pk=pk)
            if ticket:
                self.instance.tickets.add(ticket)

    class Meta:
        model = ToDo
        fields = (
            'title', 
            'body', 
            'started_on', 
            'estimate', 
            'is_deleted',
            'status', 
            'priority', 
            'component',
            'due_on',
        )

        widgets = {
            "due_on": forms.DateTimeInput(attrs={'type':'date'})
        }

