from django.utils.timezone import now
from django.test import TestCase
from django.contrib.auth.models import User, Group
from traq.projects.models import Project, Component
from traq.tickets.models import Ticket, TicketStatus, TicketPriority, Work, WorkType, Comment
from traq.todos.models import ToDo

class TraqCustomTest(TestCase):
    def setUp(self):
        super(TraqCustomTest, self).setUp()
        arc_client_group = Group(name='arcclient')
        arc_client_group.save()
        self.arc_client_group = arc_client_group

        user = User(username='raygun', first_name='bob', last_name='dole', email='bobdole@bobdole.com')
        user.set_password('foo')
        user.save()
        user.groups.add(arc_client_group)
        self.user = user 

        arc_group = Group(name='arc')
        arc_group.save()
        self.arc_group = arc_group

        # yes, that is the name of a pokemon
        admin = User(username='moltres', first_name='franklin', last_name='benjamin', email='lightningkeys@gmail.com', is_staff=True)
        admin.set_password('foo')
        admin.save()
        admin.groups.add(arc_group)
        self.admin = admin

        project = Project(
                name='foo',
                team_dynamix_id=1,
                description='this is a project',
                created_by=self.admin,
                )
        project.save()
        self.project = project

        project2 = Project(
                name='foo2',
                team_dynamix_id=2,
                description='this is another project',
                created_by=self.admin,
                )
        project2.save()
        self.project2 = project2

        component = Component(
                    name='component',
                    description='this is a description',
                    invoice_description='this is the invoice description',
                    rank=1,
                    project=self.project,
                    created_by=self.admin,
                )
        component.save()
        self.component = component

        ticket = Ticket(
                title='ticket',
                body='body',
                created_by=self.admin,
                status=TicketStatus.objects.first(),
                priority=TicketPriority.objects.first(),
                project=self.project,
                component=self.component,
                assigned_to_id=self.admin.pk
                )
        ticket.save()
        self.ticket = ticket

        ticket_2 = Ticket(
                title='ticket 2',
                body='body',
                created_by=self.user,
                status=TicketStatus.objects.first(),
                priority=TicketPriority.objects.first(),
                project=self.project,
                component=self.component,
                assigned_to_id=self.user.pk
                )
        ticket_2.save()
        self.ticket_2 = ticket_2

        ticket_3 = Ticket(
                title='ticket 3',
                body='body',
                created_by=self.admin,
                status=TicketStatus.objects.first(),
                priority=TicketPriority.objects.first(),
                project=self.project,
                component=self.component,
                assigned_to_id=self.admin.pk
                )
        ticket_3.save()
        self.ticket_3 = ticket_3

        ticket_4 = Ticket(
                title='ticket 4',
                body='body',
                created_by=self.admin,
                status=TicketStatus.objects.first(),
                priority=TicketPriority.objects.first(),
                project=self.project2,
                component=self.component,
                assigned_to_id=self.admin.pk
                )
        ticket_4.save()
        self.ticket_4 = ticket_4

        todo = ToDo(
                title='todo',
                body='body',
                created_by=self.admin,
                status_id=1,
                priority_id=TicketPriority.objects.first().pk,
                rank=1,
                component_id=self.component.pk,
                project_id=self.project.pk,
                )
        todo.save()
        self.todo = todo

        #self.todo.tickets.add(self.ticket)
        self.todo.save()

        work = Work(
            description="foo",
            billable=False,
            time='10:00:00',
            state=1,
            started_on=now(),
            done_on=now(),
            type=WorkType.objects.first(),
            ticket=self.ticket,
            created_by=self.admin,
            is_deleted=False,
        )
        work.save()
        self.work = work
