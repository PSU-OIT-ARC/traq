from django.utils.translation import gettext as _
import django_filters
from .models import ToDo  
from traq.tickets.filters import range_from_today, StartDateRangeFilter, TicketFilterSet
import datetime

class ToDoFilterSet(TicketFilterSet):
    def __init__(self, *args, **kwargs):
            super(ToDoFilterSet, self).__init__(*args, **kwargs)
            self.filters.pop('priority')
            
    class Meta:
        model = ToDo
        fields = ('status', 'due_range','sprint_end')

class ToDoPriorityFilterSet(ToDoFilterSet):
    def __init__(self, *args, **kwargs):
            super(ToDoFilterSet, self).__init__(*args, **kwargs)
            self.filters.pop('priority')
            self.filters.pop('status')
            
    class Meta:
        model = ToDo
        fields = ('due_range','sprint_end')

