from django.utils.translation import ugettext_lazy as _
from django.db.models.loading import get_model
from django.template.defaultfilters import date
import django_filters
from .models import TicketStatus, TicketPriority, Ticket, Project
from django import forms
from django.utils.timezone import  get_current_timezone, localtime, now, make_aware
import datetime

def range_from_today(interval):
    date_obj = localtime(now())
    naive_start = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0)
    naive_end = naive_start + interval

    return (
        make_aware(naive_start, get_current_timezone()),
        make_aware(naive_end, get_current_timezone())
    )

def get_choices(model):
    my_choices= []
    my_choices.append( ('',"Any ol\' Time") )
    last_month = now() - datetime.timedelta(days=30)
    items = model.objects.filter(project_id=9, due_on__gte=last_month).distinct()
    dates = items.values_list('due_on', flat='true').all()
    for due in dates:
        if due is not None:
            pretty_date = due.strftime('%d %b, %Y')
            my_choices.append( (due.date(), pretty_date) )
    return my_choices
    
class StartDateRangeFilter(django_filters.DateRangeFilter):
    options = {
        '': (_('Any Date'), lambda qs, name: qs.all()),
        1: (_('Today'), lambda qs, name: qs.filter(**{
                    '%s__range' % name: range_from_today(datetime.timedelta(days=1))
                    })),
        2: (_('Next seven days'), lambda qs, name: qs.filter(**{
                    '%s__range' % name: range_from_today(datetime.timedelta(days=7))
                    })),
        3: (_('This month'), lambda qs, name: qs.filter(**{
                    '%s__year' % name: now().year,
                    '%s__month' % name: now().month,
                    })),
        4: (_('Next three months'), lambda qs, name: qs.filter(**{
                    '%s__range' % name: range_from_today(datetime.timedelta(days=90))
                    })),
        5: (_('Next six months'), lambda qs, name: qs.filter(**{
                    '%s__range' % name: range_from_today(datetime.timedelta(days=180))
                    })),
        6: (_('This year'), lambda qs, name: qs.filter(**{
                    '%s__year' % name: now().year,
                    })),
        7: (_('Within last Month'), lambda qs, name: qs.filter(**{
                    '%s__range' % name: (now() - datetime.timedelta(days=30), now()),
                    })),
        }

    
class TicketFilterSet(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter('status', label=_('Status'), queryset=TicketStatus.objects.all())
    priority = django_filters.ModelChoiceFilter('priority', label=_('Priority'), queryset=TicketPriority.objects.all())  
    sprint_end = django_filters.DateFilter('due_on', label=_('Due On')) 
    due_range = StartDateRangeFilter('due_on', label=_('Due Date'))   


    def __init__(self, *args, **kwargs):
        super(TicketFilterSet, self).__init__(*args, **kwargs)
        self.filters['sprint_end'].widget=forms.Select(choices = get_choices(self.Meta.model) ) 

        
    class Meta:
        model = Ticket
        fields = ('status', 'priority', 'due_range', 'sprint_end')



