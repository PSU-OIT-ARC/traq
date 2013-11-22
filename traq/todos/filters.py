from django.utils.translation import gettext as _
import django_filters
from django import forms
from .models import ToDo 
from traq.projects.models import Project
from traq.tickets.filters import range_from_today, StartDateRangeFilter, TicketFilterSet, get_choices
import datetime
from django.shortcuts import get_object_or_404

class ToDoFilterSet(TicketFilterSet):
    def __init__(self, *args, **kwargs):
            super(ToDoFilterSet, self).__init__(*args, **kwargs)
            self.filters.pop('priority')
            
    class Meta:
        model = ToDo
        fields = ('status', 'due_range','sprint_end')

class ToDoPriorityFilterSet(ToDoFilterSet):
    def __init__(self, *args, **kwargs):
            project_id = kwargs.get('project_id')
            project = get_object_or_404(Project, pk=project_id)
            super(ToDoFilterSet, self).__init__(*args, **kwargs)
            extra ={'status':1}
            self.filters['sprint_end'].widget=forms.Select(choices = get_choices(self.Meta.model, project, extra)) 
            self.filters.pop('priority')
            self.filters.pop('status')
            self.filters.pop('due_range')
    class Meta:
        model = ToDo
        fields = ('due_range','sprint_end')

