from django.db import models
from ..projects.models import Project, Attribute

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    summary = models.CharField(max_length=255)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    status = models.ForeignKey(Attribute)
    project = models.ForeignKey(Project)

class Work(models.Model):
    work_id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    ticket = models.ForeignKey(Ticket)
