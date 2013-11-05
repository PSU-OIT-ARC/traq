from django.db import models
from traq.tickets.models import Ticket, TicketStatus, TicketPriority 
from django.contrib.auth.models import User
from traq.projects.models import Project, Component
from datetime import datetime
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


class ToDo(models.Model):
    ToDo_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(default=lambda:datetime.now())
    edited_on = models.DateTimeField(auto_now=True)
    estimate = models.DecimalField(null=True, default=None, max_digits=5, decimal_places=2, blank=True)
    is_deleted = models.BooleanField(default=False, verbose_name='Delete')
    due_on = models.DateTimeField(null=True, default=None, blank=True, verbose_name='Desired due date')
    tickets = models.ManyToManyField(Ticket, related_name='todos') 
    created_by = models.ForeignKey(User, related_name='+')
    status = models.ForeignKey(TicketStatus)
    rank = models.IntegerField(default=None, blank=True, null=True)
    project = models.ForeignKey(Project)
    priority = models.ForeignKey(TicketPriority)
    component = models.ForeignKey(Component)


@receiver(pre_save, sender=ToDo)
def my_handler(sender, instance, **kwargs):
    tickets = Ticket.objects.filter(todos=instance).values_list('status', flat=True)
    print tickets
    if instance.tickets.exists():
        if 1 in tickets or 2 in tickets or 3 in tickets: 
            instance.status_id = 2
        else: 
            instance.status_id = 5
    else:
        instance.status_id = 1
    


