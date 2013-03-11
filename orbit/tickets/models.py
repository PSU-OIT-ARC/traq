from itertools import chain
from datetime import timedelta, datetime
from django.db import models
from ..projects.models import Project, Component, Milestone
from django.contrib.auth.models import User
from django.utils.timezone import utc

class TicketStatusManager(models.Manager):
    def closed(self):
        return self.get(name="Closed")

class TicketStatus(models.Model):
    ticket_status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    rank = models.IntegerField()
    is_default = models.BooleanField(default=False)
    importance = models.IntegerField()

    objects = TicketStatusManager()

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

    def tickets(self):
        """Return a query set of tickets with all the useful related fields and the default ordering"""
        queryset = Ticket.objects.filter(project__is_deleted=False).select_related(
            'status', 
            'priority', 
            'assigned_to', 
            'created_by',
            'component',
            'milestone',
            'project',
        ).extra(select={
            # the sort order
            "global_order": "IF(ticket_status.importance = 0, ticket.created_on, 0)",
            # because the column name "name" is used in all these tables, alias
            # each name column with something else, so when converted to a dict,
            # the columns don't disappear
            "status_name": "ticket_status.name",
            "priority_name": "ticket_priority.name",
            "component_name": "component.name",
        }).order_by("-status__importance", "-global_order", "-priority__rank")

        return queryset

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(default=lambda:datetime.now())
    edited_on = models.DateTimeField(auto_now=True)
    estimated_time = models.TimeField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    is_extra = models.BooleanField(default=False, verbose_name="Outside scope of original proposal")
    due_on = models.DateTimeField(null=True, default=None, blank=True)

    created_by = models.ForeignKey(User, related_name='+')
    assigned_to = models.ForeignKey(User, null=True, default=None, related_name='+', blank=True)
    status = models.ForeignKey(TicketStatus)
    priority = models.ForeignKey(TicketPriority)
    project = models.ForeignKey(Project)
    component = models.ForeignKey(Component)
    milestone = models.ForeignKey(Milestone, null=True, default=None, blank=True)

    objects = TicketManager()

    def isOverDue(self):
        return self.due_on < datetime.utcnow().replace(tzinfo=utc)

    def close(self):
        """Closes a ticket, and sets all non finished work to done"""
        # finish all running work
        self.status = TicketStatus.objects.closed()
        self.save()
        work = Work.objects.filter(ticket=self).exclude(state=Work.DONE)
        had_running_work = False
        for w in work:
            w.time = w.duration()
            w.done()
            w.save()
            had_running_work = True
        return had_running_work

    def totalTimes(self, interval=()):
        """Return a dict containing timedelta objects that indicate how much
        total, billable and non_billable time has been spent on this ticket"""

        sql_where = "(1 = 1)"
        # if the caller specified an interval, use it in the query
        if interval:
            sql_where = "(work.done_on BETWEEN %s AND %s)"

        # generate the list of arguments to the query. It gets a little tricky
        # because the arguments change if an interval is specified by the
        # caller
        args = tuple(chain((self.pk, Work.DONE,), interval))*3 # times 3 because the same args are used for total, billable and non_billable

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
        """Return the default WorkType"""
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
        """Sets the state to pause for all running work created by `created_by`.
        Returns true is there was work that was running before, or false"""
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
    time = models.TimeField() # the amount of time spent on this work item
    started_on = models.DateTimeField()
    done_on = models.DateTimeField(null=True, default=None)
    state = models.IntegerField(choices=(
        (RUNNING, "Running"),
        (PAUSED, "Paused"),
        (DONE, "Done"),
    ), default=DONE)
    # helps keep track of the duration of pausing and running work
    state_changed_on = models.DateTimeField(default=None, null=True, blank=True)

    type = models.ForeignKey(WorkType)
    ticket = models.ForeignKey(Ticket)
    created_by = models.ForeignKey(User, related_name='+')

    is_deleted = models.BooleanField(default=False, verbose_name="Delete?")

    def duration(self):
        """Return a time object representing the amount of time that has been
        spent on this work item"""
        if self.state == Work.DONE:
            return self.time
        elif self.state == Work.PAUSED:
            return self.time
        elif self.state == Work.RUNNING:
            start = self.state_changed_on or self.created_on
            delta = datetime.utcnow().replace(tzinfo=utc) - start
            return (datetime.combine(datetime.today(), self.time) + delta).time()
        else:
            raise ValueError("Work object with pk=%d has an invalid work state, %d" % (self.pk, self.state))

    def pause(self):
        """Pause a running work item"""
        # you can only pause running work
        if self.state != Work.RUNNING:
            return

        self.state = Work.PAUSED
        # calculate how much time has past since this work was last continued or created
        start = self.state_changed_on or self.created_on
        delta = datetime.utcnow().replace(tzinfo=utc) - start
        t = (datetime.combine(datetime.today(), self.time) + delta).time()
        self.time = t
        self.state_changed_on = datetime.now()
        self.save()

    def continue_(self):
        """Continue work that was paused"""
        self.state = Work.RUNNING
        # this is important because it is required to calculate how much time
        # has elasped when the work is paused or set as done
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

