from itertools import chain
from datetime import timedelta, datetime
from django.db import models
from ..projects.models import Project, Component
from django.contrib.auth.models import User
from django.utils.timezone import utc

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

class TicketManager(models.Manager):
    def get_query_set(self):
        return super(TicketManager, self).get_query_set().filter(is_deleted=False)

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(default=lambda:datetime.utcnow())
    edited_on = models.DateTimeField(auto_now=True)
    estimated_time = models.TimeField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    is_extra = models.BooleanField(default=False, verbose_name="Outside scope of original proposal")

    created_by = models.ForeignKey(User, related_name='+')
    assigned_to = models.ForeignKey(User, null=True, default=None, related_name='+')
    status = models.ForeignKey(TicketStatus)
    priority = models.ForeignKey(TicketPriority)
    project = models.ForeignKey(Project)
    component = models.ForeignKey(Component)

    objects = TicketManager()

    def totalTimes(self, interval=()):
        sql_where = "(1 = 1)"
        if interval:
            sql_where = "(work.done_on BETWEEN %s AND %s)"

        args = tuple(chain((self.pk, Work.DONE,), interval))*3
        rows = Ticket.objects.raw("""
            SELECT ticket_id, 
            (SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) FROM work WHERE is_deleted = 0 AND ticket_id = %s AND work.state = %s AND """ + sql_where + """ ) AS total_time,
            (SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) FROM work WHERE is_deleted = 0 AND ticket_id = %s AND work.state = %s AND """ + sql_where + """ AND billable = 1 ) AS billable_time,
            (SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) FROM work WHERE is_deleted = 0 AND ticket_id = %s AND work.state = %s AND """ + sql_where + """ AND billable = 0 ) AS non_billable_time
            FROM ticket 
            WHERE ticket_id = %s
        """, args + (self.pk,))
        times = list(rows)[0]

        total = timedelta(seconds=int(times.total_time))
        billable = timedelta(seconds=int(times.billable_time))
        non_billable = timedelta(seconds=int(times.non_billable_time))
        return {
            'total': total,
            'billable': billable,
            'non_billable': non_billable,
        }

    class Meta:
        db_table = 'ticket'

class WorkTypeManager(models.Manager):
    def default(self):
        objs = WorkType.objects.filter(is_default=1).order_by('rank')
        if len(objs) > 0:
            return list(objs)[0]
        return None

class WorkType(models.Model):
    work_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_default = models.BooleanField(default=False)
    rank = models.IntegerField()

    objects = WorkTypeManager()

    class Meta:
        ordering = ['rank']
        db_table = 'work_type'

    def __unicode__(self):
        return u'%s' % (self.name)

class WorkManager(models.Manager):
    def get_query_set(self):
        return super(WorkManager, self).get_query_set().filter(is_deleted=False)

    def pauseRunning(self, created_by):
        other_work = Work.objects.filter(created_by=created_by, state=Work.RUNNING)
        paused_something = False
        for work in other_work:
            work.pause()
            paused_something = True

        return paused_something

class Work(models.Model):
    DONE = 0
    RUNNING = 1
    PAUSED = 2

    work_id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    billable = models.BooleanField(default=True)
    time = models.TimeField()
    started_on = models.DateTimeField()
    done_on = models.DateTimeField(null=True, default=None)
    state = models.IntegerField(choices=(
        (RUNNING, "Running"),
        (PAUSED, "Paused"),
        (DONE, "Done"),
    ), default=DONE)
    state_changed_on = models.DateTimeField(default=None, null=True, blank=True)

    type = models.ForeignKey(WorkType)
    ticket = models.ForeignKey(Ticket)
    created_by = models.ForeignKey(User, related_name='+')

    is_deleted = models.BooleanField(default=False, verbose_name="Delete?")

    def duration(self):
        if self.state == Work.DONE:
            return self.time
        elif self.state == Work.PAUSED:
            return self.time
        else:
            start = self.state_changed_on or self.created_on
            delta = datetime.utcnow().replace(tzinfo=utc) - start
            return (datetime.combine(datetime.today(), self.time) + delta).time()

    def pause(self):
        self.state = Work.PAUSED
        start = self.state_changed_on or self.created_on
        delta = datetime.utcnow().replace(tzinfo=utc) - start
        t = (datetime.combine(datetime.today(), self.time) + delta).time()
        self.time = t
        self.state_changed_on = datetime.now()
        self.save()

    def continue_(self):
        self.state = Work.RUNNING
        self.state_changed_on = datetime.now()
        self.save()

    def done(self):
        self.state = Work.DONE
        # once the done_on date is set, it should never be changed because it
        # affects the billing reports
        if self.done_on is None:
            self.done_on = datetime.now()

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

