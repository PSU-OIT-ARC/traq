from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db.models.loading import get_model
from django.template.defaultfilters import date
import django_filters
from .models import TicketStatus, TicketPriority, Ticket, Project
from django.contrib.auth.models import User
from django import forms
from django.utils.timezone import  get_current_timezone, localtime, now, make_aware
from django.shortcuts import get_object_or_404
import datetime

def range_from_today(interval):
    date_obj = localtime(now())
    naive_start = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0)
    naive_end = naive_start + interval

    return (
        make_aware(naive_start, get_current_timezone()),
        make_aware(naive_end, get_current_timezone())
    )


def get_choices(model, project=None, extra=None):      
    items = model.objects.filter(is_deleted=False)
    if project:
        items = model.objects.filter(project_id=project.pk)
    if extra:
        items = items.filter(**extra)

    # Get the explicitly set due dates
    dates = set(
        items
        .filter(due_on__isnull=False)
        .distinct()
        .values_list('due_on', flat=True)
    )

    if hasattr(model, 'milestone'):
        # Add milestone due dates (but only for tickets that don't also
        # have an explicitly set due date)
        dates |= set(
            items
            .filter(due_on__isnull=True, milestone__isnull=False)
            .distinct()
            .values_list('milestone__due_on', flat=True)
        )

    my_choices = [('', "Any Time")] + sorted((d.date(), d.strftime('%b %d, %Y')) for d in dates)
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


class DueOnFilter(django_filters.DateFilter):

    def filter(self, qs, value):
        if isinstance(value, django_filters.fields.Lookup):
            lookup = unicode(value.lookup_type)
            value = value.value
        else:
            lookup = self.lookup_type
        if value in ([], (), {}, None, ''):
            return qs
        # Custom
        tzinfo = now().tzinfo
        value = (
            datetime.datetime.combine(value, datetime.time.min).replace(tzinfo=tzinfo),
            datetime.datetime.combine(value, datetime.time.max).replace(tzinfo=tzinfo),
        )
        method = qs.exclude if self.exclude else qs.filter
        q = Q(**{'%s__%s' % (self.name, lookup): value})
        q |= Q(
            due_on__isnull=True,
            milestone__isnull=False,
            **{'milestone__%s__%s' % (self.name, lookup): value}
        )
        # /Custom
        qs = method(q)
        if self.distinct:
            qs = qs.distinct()
        return qs

    
class TicketFilterSet(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter('status', label=_('Status'), queryset=TicketStatus.objects.all())
    priority = django_filters.ModelChoiceFilter('priority', label=_('Priority'), queryset=TicketPriority.objects.all())  
    sprint_end = DueOnFilter('due_on', label=_('Due On'), lookup_type='range', distinct=True)
    due_range = StartDateRangeFilter('due_on', label=_('Due Date'))   
    assigned_to = django_filters.ModelChoiceFilter('assigned_to', label='Assigned to', queryset=User.objects.filter(is_active=True).filter(groups__name='arc')) 

    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id', None)
        if project_id is not None:
            project = get_object_or_404(Project, pk=project_id)
        else:
            project = None
        super(TicketFilterSet, self).__init__(*args, **kwargs)
        self.filters['sprint_end'].widget=forms.Select(choices = get_choices(self.Meta.model, project=project),)

    class Meta:
        model = Ticket
        fields = ('assigned_to', 'status', 'priority', 'due_range', 'sprint_end')



