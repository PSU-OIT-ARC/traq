from django.utils.translation import ugettext_lazy as _
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
        }

class SprintEndRangeFilter(django_filters.DateRangeFilter):
    my_choices = {'': (_('Any ol\' Time'), lambda qs, name: qs.all())}
    tix = Ticket.objects.filter(project_id=9)
    dates = tix.values_list('due_on', flat='true').all()
    index = 1
    for due in dates:
        if due is not None:
            pretty_date = due.strftime('%d %b, %Y')
            my_choices[index] = (pretty_date, lambda qs, name, due=due: qs.filter(**{
                '%s__day' % name: due.day, 
                '%s__month' % name: due.month, 
                '%s__year' % name: due.year 
                }))
            index += 1
    options = my_choices

   
class TicketFilterSet(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter('status', label=_('Status'), queryset=TicketStatus.objects.all())
    priority = django_filters.ModelChoiceFilter('priority', label=_('Priority'), queryset=TicketPriority.objects.all())  
    sprint_end = SprintEndRangeFilter('due_on', label=_('Due On:'))
    due_range = StartDateRangeFilter('due_on', label=_('Due Date'))   
    class Meta:
        model = Ticket
        fields = ('status', 'priority', 'due_range', 'sprint_end')


