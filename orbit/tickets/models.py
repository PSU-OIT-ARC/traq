from django.db import models
from ..projects.models import Project, Attribute
from django.contrib.auth.models import User
from datetime import timedelta

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    estimated_time = models.TimeField(null=True, default=None)

    created_by = models.ForeignKey(User, related_name='+')
    assigned_to = models.ForeignKey(User, null=True, default=None, related_name='+')
    status = models.ForeignKey(Attribute, related_name="+")
    priority = models.ForeignKey(Attribute, related_name="+")
    project = models.ForeignKey(Project, related_name="+")

    def totalTimes(self):
        rows = Ticket.objects.raw("""
            SELECT ticket_id, 
            (SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) FROM tickets_work WHERE ticket_id = %s) AS total_time,
            (SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) FROM tickets_work WHERE ticket_id = %s AND billable = 1) AS billable_time,
            (SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) FROM tickets_work WHERE ticket_id = %s AND billable = 0) AS non_billable_time

            FROM tickets_ticket 
            WHERE ticket_id = %s
        """, (self.pk, self.pk, self.pk, self.pk))
        times = list(rows)[0]

        total = timedelta(seconds=int(times.total_time))
        billable = timedelta(seconds=int(times.billable_time))
        non_billable = timedelta(seconds=int(times.non_billable_time))
        return {
            'total': total,
            'billable': billable,
            'non_billable': non_billable
        }

class WorkManager(models.Manager):
    def get_query_set(self):
        return super(WorkManager, self).get_query_set().filter(is_deleted=False)

class Work(models.Model):
    work_id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    billable = models.BooleanField(default=True)
    time = models.TimeField()

    type = models.ForeignKey(Attribute, related_name="+")
    ticket = models.ForeignKey(Ticket)
    created_by = models.ForeignKey(User, related_name='+')

    is_deleted = models.BooleanField(default=False, verbose_name="Delete?")

    objects = WorkManager()

class CommentManager(models.Manager):
    def get_query_set(self):
        return super(CommentManager, self).get_query_set().filter(is_deleted=False)

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Delete?")

    ticket = models.ForeignKey(Ticket)
    created_by = models.ForeignKey(User, related_name='+')

    objects = CommentManager()

    class Meta:
        ordering = ['created_on']

