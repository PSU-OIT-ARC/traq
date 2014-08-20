from django.utils.translation import gettext as _
import django_filters
from django.http import QueryDict
from django import forms
from django.contrib.auth.models import User
from .models import ToDo 
from traq.projects.models import Project
from traq.tickets.filters import range_from_today, StartDateRangeFilter, TicketFilterSet, get_choices
import datetime
from django.shortcuts import get_object_or_404

class CustomBooleanFilter(django_filters.BooleanFilter):
    def filter(self, qs, value):
        if value is not None:
            qs = qs.exclude(**{'%s__%s' % (self.name, self.lookup_type): value})
            return qs
        return qs

class ToDoFilterSet(TicketFilterSet):
    def __init__(self, *args, **kwargs):
            super(ToDoFilterSet, self).__init__(*args, **kwargs)
            self.filters.pop('priority')
            self.filters.pop('assigned_to')
            
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
            self.filters.pop('assigned_to')

    class Meta:
        model = ToDo
        fields = ('due_range','sprint_end')

class BacklogFilterSet(ToDoPriorityFilterSet):
    estimate = CustomBooleanFilter('estimate', label=_('Estimated'), lookup_type='isnull') 
    
    def __init__(self, *args, **kwargs):
        
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)
        super(ToDoFilterSet, self).__init__(*args, **kwargs)
        extra ={'status':1}
        if not self.data:
            qdict = QueryDict('sprint_end=%s&estimate=%s' % (project.backlog(), False)) 
            print qdict
            self.data = qdict
        self.filters['sprint_end'].widget=forms.Select(choices = get_choices(self.Meta.model, project, extra)) 
        
        self.filters.pop('status')
        self.filters.pop('priority')
        self.filters.pop('due_range')
        self.filters.pop('assigned_to')

    class Meta:
        model = ToDo
        fields = ('due_range','sprint_end', 'estimate')


