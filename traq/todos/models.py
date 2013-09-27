from django.db import models
from traq.tickets.models import Ticket, TicketStatus, TicketPriority 
from django.contrib.auth.models import User
from traq.projects.models import Project, Component
from datetime import datetime

class ToDo(models.Model):
    ToDo_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(default=lambda:datetime.now())
    edited_on = models.DateTimeField(auto_now=True)
    estimate = models.DecimalField(null=True, default=None, max_digits=5, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    due_on = models.DateTimeField(null=True, default=None, blank=True, verbose_name='Desired due date')
    tickets = models.ManyToManyField(Ticket, related_name='todos') 
    created_by = models.ForeignKey(User, related_name='+')
    status = models.ForeignKey(TicketStatus)
    priority = models.IntegerField(default=None, blank=True, null=True)
    project = models.ForeignKey(Project)
    component = models.ForeignKey(Component)

