from django.utils.translation import ugettext_lazy as _

import django_filters

from .models import TicketStatus, TicketPriority, Ticket


class TicketFilterSet(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter('status', label=_('Status'), queryset=TicketStatus.objects.all())
    priority = django_filters.ModelChoiceFilter('priority', label=_('Priority'), queryset=TicketPriority.objects.all())

    class Meta:
        model = Ticket
        fields = ('status', 'priority')
