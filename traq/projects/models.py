import math
import json
from pytz import timezone
from django.conf import settings as SETTINGS
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import utc
from ..utils import dictfetchall, jsonhandler


class ProjectManager(models.Manager):
    def get_query_set(self):
        return super(ProjectManager, self).get_query_set().filter(is_deleted=False)

    def timeByUser(self, user, interval=()):
        sql_where = "(1 = 1)"
        if interval:
            sql_where = "(work.done_on BETWEEN %s AND %s)"

        rows = self.raw("""
        SELECT 
            project.*,
            SUM(TIME_TO_SEC(IFNULL(`work`.`time`, 0))) AS total_time,
            SUM(IF(`work`.billable, TIME_TO_SEC(IFNULL(`work`.`time`, 0)), 0)) AS billable_time,
            SUM(IF(`work`.billable = 0, TIME_TO_SEC(IFNULL(`work`.`time`, 0)), 0)) AS non_billable_time
        FROM 
            ticket 
        INNER JOIN 
            work 
        ON 
            work.ticket_id = ticket.ticket_id AND 
            work.is_deleted = 0 AND
            """ + sql_where + """ AND 
            work.created_by_id = %s  
        RIGHT JOIN 
            project 
        ON 
            project.project_id = ticket.project_id AND 
            ticket.is_deleted = 0
        WHERE project.is_deleted = 0
        GROUP BY project.project_id
        ORDER BY project.name
        """, interval + (user.pk,))

        modified_rows = []
        for row in rows:
            row.total = timedelta(seconds=int(row.total_time))
            row.billable = timedelta(seconds=int(row.billable_time))
            row.non_billable = timedelta(seconds=int(row.non_billable_time))
            modified_rows.append(row)

        return modified_rows

class Project(models.Model):
    ACTIVE = 1
    INACTIVE = 0
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    pm_email = models.BooleanField(default=False, help_text="Elect to receive email notifications")
    pm = models.ForeignKey(User, null=True, default=None, related_name='+', blank=True, verbose_name="Project Lead")
    status = models.IntegerField(choices=(
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
    ), default=ACTIVE)

    # add all the meta fields here, make sure they aren't required
    point_of_contact = models.TextField(blank=True, default="", help_text="Displayed on the invoice")
    # displayed on the invoice
    invoice_description = models.TextField(blank=True, default="", help_text="Displayed on the invoice")
    # catch all
    catch_all = models.TextField(blank=True, default="", help_text="Anything you want to document here")
    # technical
    technical = models.TextField(blank=True, default="", help_text="Technical stuff")
    created_by = models.ForeignKey(User, related_name='+')
    objects = ProjectManager()
    clients = models.ManyToManyField(User, blank=True, null=True)
    estimated_hours = models.IntegerField(null=True, default=None, blank=True)
    is_scrum = models.BooleanField(default=False, help_text='This turns on a bunch of annoying Scrum things') 
    current_sprint_start = models.DateField(null=True, blank=True, verbose_name="Sprint Start")  
    current_sprint_end = models.DateField(null=True, blank=True, verbose_name="Sprint End")


    def __unicode__(self):
        return "%s" % self.name

    def createDefaultComponents(self):
        """Create all the default components for a project"""
        components = [
            "Base Site", 
            "Project Management", 
            "Themeing",
        ]

        for i, name in enumerate(components):
            c = Component(name=name, rank=i, is_default=(i == 0), project=self, created_by=self.created_by)
            c.save()

    def defaultComponent(self):
        """Return the default component"""
        comps = Component.objects.filter(project=self, is_default=1).order_by('rank')
        if len(comps) > 0:
            return list(comps)[0]
        return None

    # interval is a 2-tuple datetime start, and datetime end
    def components(self, interval=()):
        """Return the list of components in this project, including the amount
        of total, billable and non_billable time spent on the component. A
        datetime interval can be specified by the caller to limit the total,
        billable and non_billable time calculations"""
        sql_where = "(1 = 1)"
        if interval:
            sql_where = "(work.done_on BETWEEN %s AND %s)"

        rows = Component.objects.raw("""
            SELECT 
                component.*,
                IFNULL(SUM(TIME_TO_SEC(`time`)), 0) AS total_time,
                IFNULL(SUM(IF(work.billable, TIME_TO_SEC(`time`), 0)), 0) AS billable_time,
                IFNULL(SUM(IF(work.billable = 0, TIME_TO_SEC(`time`), 0)), 0) AS non_billable_time
            FROM
                component
            LEFT JOIN ticket ON ticket.component_id = component.component_id AND ticket.project_id = %s AND ticket.is_deleted = 0
            LEFT JOIN `work` ON `work`.ticket_id = ticket.ticket_id AND `work`.is_deleted = 0 AND `work`.state = %s
            WHERE
                component.project_id = %s AND
                component.is_deleted = 0 AND
                """ + sql_where + """
            GROUP BY 
                component.component_id
        """, (self.pk, Work.DONE, self.pk) + interval)

        modified_rows = [] 
        # augment all the rows with timedeltas 
        for row in rows:
            row.total = timedelta(seconds=int(row.total_time))
            row.billable = timedelta(seconds=int(row.billable_time))
            row.non_billable = timedelta(seconds=int(row.non_billable_time))
            modified_rows.append(row)

        return modified_rows

    # interval is a 2-tuple datetime start, and datetime end
    def totalCost(self, interval=()):
        """Return the total cost of a project by adding up all the work on the
        project. The caller can specify an interval to limit the calculation"""
        sql_where = "(1 = 1)"
        if interval:
            sql_where = "(work.done_on BETWEEN %s AND %s)"

        rows = Project.objects.raw("""
            SELECT project_id, SUM(total_cost) AS total_cost FROM (
            SELECT
                CEIL(SUM(TIME_TO_SEC(IFNULL(work.time, 0)))/3600.0) * IFNULL(price, 0) AS total_cost,
                project.project_id
            FROM
                `work`
            INNER JOIN
                work_type ON work.type_id = work_type.work_type_id
            INNER JOIN
                ticket ON work.ticket_id = ticket.ticket_id
            INNER JOIN
                project ON ticket.project_id = project.project_id
            WHERE
                project.project_id = %s AND
                work.billable = 1 AND
                work.state = %s AND
                work.is_deleted = 0 AND
                ticket.is_deleted = 0 AND
                """ + sql_where + """
            GROUP BY work.type_id
            )k 
        """, (self.pk, Work.DONE) + interval)
        return rows[0].total_cost

    def latestWork(self, n):
        return Work.objects.filter(ticket__project=self, state=Work.DONE, ticket__is_deleted=False).select_related('created_by', 'type')[:n]

    def tickets(self):
        rows = Ticket.objects.tickets().filter(project=self)
        return rows

    def users(self):
        queryset = User.objects.raw("""
        SELECT DISTINCT auth_user.* 
        FROM ticket
        INNER JOIN work on work.ticket_id = ticket.ticket_id
        INNER JOIN auth_user ON work.created_by_id = auth_user.id
        WHERE project_id = %s AND
        ticket.is_deleted = 0 AND
        work.is_deleted = 0
        ORDER BY auth_user.username
        """, (self.pk,))
        return queryset

    class Meta:
        db_table = 'project'
        ordering = ['name']
        permissions = (
                ('can_view_all', "Can view all projects"),
                )

class ComponentManager(models.Manager):
    def get_query_set(self):
        return super(ComponentManager, self).get_query_set().filter(is_deleted=False)

    def timeByUser(self, project, user, interval=()):
        sql_where = "(1 = 1)"
        if interval:
            sql_where = "(work.done_on BETWEEN %s AND %s)"

        rows = self.raw("""
        SELECT 
            component.*,
            SUM(TIME_TO_SEC(IFNULL(`work`.`time`, 0))) AS total_time,
            SUM(IF(`work`.billable, TIME_TO_SEC(IFNULL(`work`.`time`, 0)), 0)) AS billable_time,
            SUM(IF(`work`.billable = 0, TIME_TO_SEC(IFNULL(`work`.`time`, 0)), 0)) AS non_billable_time
        FROM 
            ticket 
        INNER JOIN 
            work on work.ticket_id = ticket.ticket_id AND 
            work.is_deleted = 0 AND
            """ + sql_where + """ AND 
            work.created_by_id = %s  
        RIGHT JOIN 
            component ON component.component_id = ticket.component_id AND ticket.is_deleted = 0
        WHERE 
            component.project_id = %s AND component.is_deleted = 0
        GROUP BY component.component_id
        ORDER BY component.rank
        """, interval + (user.pk, project.pk))

        modified_rows = []
        for row in rows:
            row.total = timedelta(seconds=int(row.total_time))
            row.billable = timedelta(seconds=int(row.billable_time))
            row.non_billable = timedelta(seconds=int(row.non_billable_time))
            modified_rows.append(row)

        return modified_rows

class Component(models.Model):
    component_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)
    invoice_description = models.TextField(default="", blank=True)
    rank = models.IntegerField()
    is_default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    project = models.ForeignKey(Project)
    created_by = models.ForeignKey(User, related_name='+')

    objects = ComponentManager()

    def invoiceBreakdown(self, interval=()):
        """Return a list of dicts containing the total amount of time and money
        spent per work_type on this component"""
        sql_where = "(1 = 1)"
        if interval:
            sql_where = "(work.done_on BETWEEN %s AND %s)"
        rows = Component.objects.raw("""
            SELECT IFNULL(SUM(TIME_TO_SEC(`time`)), 0) AS total_time, price, component.*
            FROM 
                `work` 
            INNER JOIN 
                work_type ON work.type_id = work_type.work_type_id
            INNER JOIN 
                ticket ON work.ticket_id = ticket.ticket_id
            INNER JOIN
                component ON ticket.component_id = component.component_id
            WHERE 
                billable = 1 AND
                state = %s AND 
                work.is_deleted = 0 AND
                ticket.is_deleted = 0 AND
                component.component_id = %s AND
                """ + sql_where + """
            GROUP BY work_type_id, component_id
            ORDER BY component.rank
        """, (Work.DONE, self.pk) + interval)
        
        info = []
        for row in rows:
            td = timedelta(seconds=int(row.total_time))
            rate = row.price
            hours = int(td.days * 24 + math.ceil(td.seconds / 3600.0))
            bill = rate * hours
            info.append({"rate": rate, "hours": hours, "bill": bill})
        return info

    class Meta:
        db_table = 'component'
        ordering = ['rank']

    def __unicode__(self):
        return u'%s' % (self.name)

class MilestoneManager(models.Manager):
    def get_query_set(self):
        return super(MilestoneManager, self).get_query_set().filter(is_deleted=False)

class Milestone(models.Model):
    milestone_id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    due_on = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, related_name="+")
    project = models.ForeignKey(Project)

    objects = MilestoneManager()

    class Meta:
        db_table = 'milestone'
        ordering = ['due_on']

    def __unicode__(self):
        utc_date = self.due_on.replace(tzinfo=utc)
        tz = timezone(SETTINGS.TIME_ZONE)
        return u'%s %s' % (self.name, utc_date.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")) 


# circular dependance problem
from ..tickets.models import Ticket, Work


