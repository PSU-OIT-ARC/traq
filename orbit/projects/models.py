from datetime import timedelta
from django.db import models

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    def createDefaultComponents(self):
        components = [
            "Base Site", 
            "Project Management", 
            "Themeing",
        ]

        for i, name in enumerate(components):
            c = Component(name=name, rank=i, is_default=(i == 0), project=self)
            c.save()

    def defaultComponent(self):
        return Component.objects.get(project=self, is_default=1)

    def latestWork(self, n):
        return Work.objects.filter(ticket__project=self).select_related('created_by', 'type')[:n]

    def tickets(self):
        rows = Ticket.objects.filter(project=self).select_related(
            'status', 
            'priority', 
            'assigned_to', 
            'created_by',
            'component',
        ).extra(select={
            "global_order": "IF(ticket_status.importance = 0, ticket.created_on, 0)"
        }).order_by("-status__importance", "-global_order", "-priority__rank")
        return rows

    class Meta:
        db_table = 'project'

class ComponentManager(models.Manager):
    def withTimes(self, project):
        rows = Component.objects.raw("""
            SELECT 
                component.*,
                IFNULL(SUM(TIME_TO_SEC(`time`)), 0) AS total_time,
                IFNULL(SUM(IF(work.billable, TIME_TO_SEC(`time`), 0)), 0) AS billable_time,
                IFNULL(SUM(IF(work.billable = 0, TIME_TO_SEC(`time`), 0)), 0) AS non_billable_time
            FROM
                component
            LEFT JOIN ticket ON ticket.component_id = component.component_id AND ticket.project_id = %s 
            LEFT JOIN `work` ON `work`.ticket_id = ticket.ticket_id
            WHERE
                component.project_id = %s
            GROUP BY 
                component.component_id
        """, (project.pk, project.pk))

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
    rank = models.IntegerField()
    is_default = models.BooleanField(default=False)
    project = models.ForeignKey(Project)

    objects = ComponentManager()

    class Meta:
        db_table = 'component'
        ordering = ['rank']

    def __unicode__(self):
        return u'%s' % (self.name)

# circular dependance problem
from ..tickets.models import Ticket, Work
