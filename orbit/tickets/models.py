from django.db import models
from ..projects.models import Project, Component
from django.contrib.auth.models import User
from datetime import timedelta

class TicketStatus(models.Model):
    ticket_status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    rank = models.IntegerField()
    is_default = models.BooleanField(default=False)
    importance = models.IntegerField()

    class Meta:
        ordering = ['rank']
        db_table = 'ticket_status'

    def __unicode__(self):
        return u'%s' % (self.name)

class TicketPriority(models.Model):
    ticket_priority_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    rank = models.IntegerField()
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['rank']
        db_table = 'ticket_priority'

    def __unicode__(self):
        return u'%s' % (self.name)

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    estimated_time = models.TimeField(null=True, default=None)

    created_by = models.ForeignKey(User, related_name='+')
    assigned_to = models.ForeignKey(User, null=True, default=None, related_name='+')
    status = models.ForeignKey(TicketStatus)
    priority = models.ForeignKey(TicketPriority)
    project = models.ForeignKey(Project)
    component = models.ForeignKey(Component, null=True, default=None)

    def totalTimes(self):
        rows = Ticket.objects.raw("""
            SELECT ticket_id, 
            (SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) FROM work WHERE ticket_id = %s) AS total_time,
            (SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) FROM work WHERE ticket_id = %s AND billable = 1) AS billable_time,
            (SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) FROM work WHERE ticket_id = %s AND billable = 0) AS non_billable_time

            FROM ticket 
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

    class Meta:
        db_table = 'ticket'

class WorkManager(models.Manager):
    def get_query_set(self):
        return super(WorkManager, self).get_query_set().filter(is_deleted=False)

class WorkType(models.Model):
    work_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_default = models.BooleanField(default=False)
    rank = models.IntegerField()

    class Meta:
        ordering = ['rank']
        db_table = 'work_type'

    def __unicode__(self):
        return u'%s' % (self.name)


class Work(models.Model):
    work_id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    billable = models.BooleanField(default=True)
    time = models.TimeField()

    type = models.ForeignKey(WorkType)
    ticket = models.ForeignKey(Ticket)
    created_by = models.ForeignKey(User, related_name='+')

    is_deleted = models.BooleanField(default=False, verbose_name="Delete?")

    class Meta:
        db_table = 'work'
        ordering = ['-created_on']
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
        db_table = 'comment'

