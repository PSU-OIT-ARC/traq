from django.utils.translation import ugettext_lazy as _
import django_filters
from .models import TicketStatus, TicketPriority, Ticket
from django import forms

class TicketFilterSet(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter('status', label=_('Status'), queryset=TicketStatus.objects.all())
    priority = django_filters.ModelChoiceFilter('priority', label=_('Priority'), queryset=TicketPriority.objects.all())
    due_on = django_filters.DateTimeFilter('due_on', label=_('Due Date'), widget=forms.DateTimeInput(attrs={'type':'date'}))
    
    class Meta:
        model = Ticket
        fields = ('status', 'priority', 'due_on')


