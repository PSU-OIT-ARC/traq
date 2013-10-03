import django_filters
from .models import ToDo  
from traq.tickets.filters import range_from_today, StartDateRangeFilter, SprintEndRangeFilter, TicketFilterSet
import datetime

class ToDoFilterSet(TicketFilterSet):
    def __init__(self, *args, **kwargs):
            super(ToDoFilterSet, self).__init__(*args, **kwargs)
            self.filters.pop('priority')

    class Meta:
        model = ToDo
        fields = ('status', 'due_range', 'sprint_end')


