from itertools import chain
from datetime import timedelta, datetime
from django.utils.timezone import now
from django.conf import settings as SETTINGS
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import utc
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from ..projects.models import Project, Component, Milestone
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

class TicketStatus(models.Model):
    ticket_status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    rank = models.IntegerField()
    is_default = models.BooleanField(default=False)
    importance = models.IntegerField()

    class Meta:
        ordering = ['rank']
        db_table = 'ticket_status'

    def __str__(self):
        return u'%s' % (self.name)

class TicketPriority(models.Model):
    ticket_priority_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    rank = models.IntegerField()
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['rank']
        db_table = 'ticket_priority'

    def __str__(self):
        return u'%s' % (self.name)

class TicketType(models.Model):
    ticket_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True, default=None)

    def __str__(self):
        return u'%s' % (self.name)

class TicketManager(models.Manager):
    def get_queryset(self):
        return super(TicketManager, self).get_queryset().filter(is_deleted=False)

    def tickets(self):
        """Return a query set of tickets with all the useful related fields and
        the default ordering"""
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
            # the columns don't collide
            "status_name": "ticket_status.name",
            "priority_name": "ticket_priority.name",
            "component_name": "component.name",
        }).order_by("-status__importance", "-global_order", "-priority__rank")

        return queryset

    def previous_ticket(self, ticket, user):
        return Ticket.objects.filter(pk__lt=ticket.pk, assigned_to_id=user.pk).order_by("-pk").first() 

    def next_ticket(self, ticket, user):
        return Ticket.objects.filter(pk__gt=ticket.pk, assigned_to_id=user.pk).order_by("pk").first()

class Ticket(models.Model):
    # the horror, the horror...too many fields
    ticket_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(default=now)
    edited_on = models.DateTimeField(auto_now=True)
    estimated_time = models.TimeField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    is_extra = models.BooleanField(default=False, verbose_name="Outside scope of original proposal")
    due_on = models.DateTimeField(null=True, default=None, blank=True)
    is_internal = models.BooleanField(default=False, verbose_name="Mark as an internal ticket (this doesn't affect any reports yet)")

    # git fields
    release = models.CharField(max_length=255, blank=True)
    branch = models.CharField(max_length=255, blank=True)

    created_by = models.ForeignKey(User, related_name='+')
    assigned_to = models.ForeignKey(User, null=True, default=None, related_name='+', blank=True)
    status = models.ForeignKey(TicketStatus)
    priority = models.ForeignKey(TicketPriority)
    project = models.ForeignKey(Project)
    component = models.ForeignKey(Component)
    milestone = models.ForeignKey(Milestone, null=True, default=None, blank=True)

    type = models.ForeignKey(TicketType, null=True, blank=True)
    
    objects = TicketManager()

    @property
    def due(self):
        """Return due_on or milestone.due_on or None."""
        if self.due_on:
            return self.due_on
        elif self.milestone:
            return self.milestone.due_on

    def isOverDue(self):
        return False if self.due_on is None else self.due_on < now()

    def finishWork(self):
        work = Work.objects.filter(ticket=self).exclude(state=Work.DONE)
        had_running_work = False
        for w in work:
            w.time = w.duration()
            w.done()
            w.save()
            had_running_work = True
        return had_running_work

    def originalState(self):
        if self.pk is None:
            return Ticket()
        return Ticket.objects.get(pk=self.pk)

    def save(self, *args, **kwargs):
        original = self.originalState()
        super(Ticket, self).save(*args, **kwargs)

        is_new = original.pk is None
        is_done = self.status_id == 4 or self.status_id == 5

        # send a notification for a new ticket, or one that was assigned
        if is_new or original.assigned_to_id != self.assigned_to_id:
            self.sendNotification('New')
        if is_done:
            self.sendNotification(self.status)

        if not is_new:
            # close all the running work on this ticket if it just turned to Completed or closed
            status_changed = self.status != original.status
            if status_changed and self.status:
                status = self.status.name
                if status in ['Completed', 'Closed']:
                    self.finishWork()


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

    def sendNotification(self, *args):
        status = args[0]
        """Send a notification email to the person assigned to this ticket"""
        if self.assigned_to:
            to = self.assigned_to.username + "@" + SETTINGS.EMAIL_DOMAIN
            ticket_url = SETTINGS.BASE_URL + reverse('tickets-detail', args=(self.pk,))
            context = {
                "ticket": self,
                "ticket_url": ticket_url,
                "username": self.assigned_to.username
            }
            text_content = render_to_string('tickets/notification.txt', context)
            html_content = render_to_string('tickets/notification.html', context)
            clean_title = re.sub(r"[\r\n]+", "; ", self.title)
            subject = 'Traq: %s Ticket #%d %s' % (status, self.pk, clean_title)

            msg = EmailMultiAlternatives(subject, text_content, 'traq@pdx.edu', [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
    
    def __str__(self):
        return u'#%s: %s' % (self.pk, self.title) 

    class Meta:
        db_table = 'ticket'

class TicketFile(models.Model):
    """Tickets can have associated files Note: this is also used for ToDo Item files"""
    file_id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to="%Y-%m")
    uploaded_on = models.DateTimeField(auto_now_add=True)

    uploaded_by = models.ForeignKey(User, related_name="+")
    ticket = models.ForeignKey(Ticket)
    todo = models.ForeignKey('todos.ToDo')
    class Meta:
        db_table = "ticket_file"
        ordering = ['file']

    def __str__(self):
        return u'%s' % (self.file.name)

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

    def __str__(self):
        return u'%s' % (self.name)

class WorkManager(models.Manager):
    def get_queryset(self):
        return super(WorkManager, self).get_queryset().filter(is_deleted=False)

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
            # since the clock is still ticking, we need to calculate the amount
            # of time since the work was paused, or created_on
            start = self.state_changed_on or self.created_on
            delta = now() - start
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
        delta = now() - start
        t = (datetime.combine(datetime.today(), self.time) + delta).time()
        self.time = t
        self.state_changed_on = now()
        self.save()

    def continue_(self):
        """Continue work that was paused"""
        self.state = Work.RUNNING
        # this is important because it is required to calculate how much time
        # has elasped when the work is paused or set as done
        self.state_changed_on = now()
        self.save()

    def done(self):
        self.state = Work.DONE
        # once the done_on date is set, it should never be changed because it
        # affects the billing reports
        if self.done_on is None:
            self.done_on = now()

    class Meta:
        db_table = 'work'
        ordering = ['-created_on']
    objects = WorkManager()

class CommentManager(models.Manager):
    def get_queryset(self):
        return super(CommentManager, self).get_queryset().filter(is_deleted=False)

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Delete?")
    todo = models.ForeignKey('todos.ToDo', null=True)
    ticket = models.ForeignKey(Ticket, null=True)
    created_by = models.ForeignKey(User, related_name='+')
    objects = CommentManager()
    

    def sendNotification(self, cc=None):
        """Send a notification email to the pm when a comment is made on  this ticket"""
        to = []
        if self.body is not None:
            if self.cc is not None:
                for cc in self.cc:
                    to.append(cc.username + '@' + SETTINGS.EMAIL_DOMAIN)
            if self.ticket is not None:
                item = 'Ticket'
                ticket = self.ticket or None
                ticket_url = SETTINGS.BASE_URL + reverse('tickets-detail', args=(ticket.pk,))
                if self.ticket.assigned_to:
                    if not self.created_by == self.ticket.assigned_to:
                        to.append(self.ticket.assigned_to.username +"@" + SETTINGS.EMAIL_DOMAIN)
            else:
                item = 'To Do'
                ticket = self.todo or None  
                ticket_url = SETTINGS.BASE_URL + reverse('todos-detail', args=(ticket.pk,))
            project = ticket.project
            if project.clients:
                if self.todo:
                    for client in project.clients.all():
                        to.append(client.username + "@" + SETTINGS.EMAIL_DOMAIN)

           # if there is no PM, there is no place to send the email
            if project.pm is None:
                return
            to.append(project.pm.username + "@" + SETTINGS.EMAIL_DOMAIN)
            
            body = render_to_string('tickets/comment_notification.txt', {
                "ticket": ticket,
                "ticket_url": ticket_url, 
                "author" : self.created_by,
                "comment_body": self.body,
            })

            clean_title = re.sub(r"[\r\n]+", "; ", ticket.title)
            subject = 'Traq New Comment: %s #%d %s' % (item, ticket.pk, clean_title)
            if project.pm_email:
                text_content = body
                html_content = body
                msg = EmailMultiAlternatives(subject, text_content, 'traq@pdx.edu', to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

    def save(self, *args, **kwargs):
        is_new = self.pk
        super(Comment, self).save(*args, **kwargs)
        if is_new is None:
            self.sendNotification()

    class Meta:
        ordering = ['created_on']
        db_table = 'comment'


@receiver(post_save, sender=Ticket)
def my_handler(sender, instance, **kwargs):
    if instance.todos.all():
        for todo in instance.todos.all():
            todo.due_on = instance.due
            tic = Ticket.objects.filter(todos=todo).values_list('status', flat=True)
            if 1 in tic or 2 in tic or 3 in tic: 
                todo.status_id=2
            else: 
                todo.status_id = 5
            todo.save()

