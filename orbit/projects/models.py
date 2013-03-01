import math
import json
from datetime import timedelta
from django.db import models
from django.db import connection
from django.contrib.auth.models import User
from ..utils import dictfetchall, jsonhandler

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    # add all the meta fields here, make sure they aren't required
    point_of_contact = models.TextField(blank=True, default="")
    # displayed on the invoice
    invoice_description = models.TextField(blank=True, default="")

    created_by = models.ForeignKey(User, related_name='+')

    def createDefaultComponents(self):
        components = [
            "Base Site", 
            "Project Management", 
            "Themeing",
        ]

        for i, name in enumerate(components):
            c = Component(name=name, rank=i, is_default=(i == 0), project=self, created_by=self.created_by)
            c.save()

    def defaultComponent(self):
        comps = Component.objects.filter(project=self, is_default=1).order_by('rank')
        if len(comps) > 0:
            return list(comps)[0]
        return None

    def components(self):
        rows = Component.objects.raw("""
            SELECT 
                component.*,
                IFNULL(SUM(TIME_TO_SEC(`time`)), 0) AS total_time,
                IFNULL(SUM(IF(work.billable, TIME_TO_SEC(`time`), 0)), 0) AS billable_time,
                IFNULL(SUM(IF(work.billable = 0, TIME_TO_SEC(`time`), 0)), 0) AS non_billable_time
            FROM
                component
            LEFT JOIN ticket ON ticket.component_id = component.component_id AND ticket.project_id = %s 
            LEFT JOIN `work` ON `work`.ticket_id = ticket.ticket_id AND `work`.is_deleted = 0 AND `work`.state = %s
            WHERE
                component.project_id = %s AND
                component.is_deleted = 0
            GROUP BY 
                component.component_id
        """, (self.pk, Work.DONE, self.pk))

        modified_rows = [] 
        for row in rows:
            row.total = timedelta(seconds=int(row.total_time))
            row.billable = timedelta(seconds=int(row.billable_time))
            row.non_billable = timedelta(seconds=int(row.non_billable_time))
            modified_rows.append(row)

        return modified_rows

    def totalCost(self):
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
                ticket.is_deleted = 0
            GROUP BY work.type_id
            )k 
        """, (self.pk, Work.DONE))
        return rows[0].total_cost

    def latestWork(self, n):
        return Work.objects.filter(ticket__project=self, state=Work.DONE).select_related('created_by', 'type')[:n]

    def tickets(self, to_json=False):
        rows = Ticket.objects.filter(project=self).select_related(
            'status', 
            'priority', 
            'assigned_to', 
            'created_by',
            'component',
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

        if not to_json:
            return rows

        cursor = connection.cursor()
        cursor.execute(str(rows.query))
        return json.dumps(dictfetchall(cursor), default=jsonhandler)

    class Meta:
        db_table = 'project'

class ComponentManager(models.Manager):
    def get_query_set(self):
        return super(ComponentManager, self).get_query_set().filter(is_deleted=False)

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

    def invoiceBreakdown(self):
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
                state = 0 AND 
                work.is_deleted = 0 AND
                ticket.is_deleted = 0 AND
                component.component_id = %s
            GROUP BY work_type_id, component_id
            ORDER BY component.rank
        """, self.pk)
        
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

# circular dependance problem
from ..tickets.models import Ticket, Work
