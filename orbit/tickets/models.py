from django.db import models
from ..projects.models import Project, Attribute
from django.contrib.auth.models import User

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(User, related_name='+')
    assigned_to = models.ForeignKey(User, null=True, default=None, related_name='+')
    status = models.ForeignKey(Attribute, related_name="+")
    priority = models.ForeignKey(Attribute, related_name="+")
    project = models.ForeignKey(Project, related_name="+")

class Work(models.Model):
    work_id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    ticket = models.ForeignKey(Ticket)

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    ticket = models.ForeignKey(Ticket)
    created_by = models.ForeignKey(User, related_name='+')

