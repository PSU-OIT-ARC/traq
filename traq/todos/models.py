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
    estimated_time = models.TimeField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    due_on = models.DateTimeField(null=True, default=None, blank=True, verbose_name='Desired due date')
    tickets = models.ManyToManyField(Ticket) 
    created_by = models.ForeignKey(User, related_name='+')
    status = models.ForeignKey(TicketStatus)
    priority = models.ForeignKey(TicketPriority)
    project = models.ForeignKey(Project)
    component = models.ForeignKey(Component)

