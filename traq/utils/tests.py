from django.test import TestCase
from django.contrib.auth.models import User
from traq.projects.models import Project, Component
from traq.tickets.models import Ticket, TicketStatus, TicketPriority


class TraqCustomTest(TestCase):
    def setUp(self):
        super(TraqCustomTest, self).setUp()

        user = User(username='raygun', first_name='bob', last_name='dole', email='bobdole@bobdole.com')
        user.set_password('foo')
        user.save()
        self.user = user

        admin = User(username='moltres', first_name='franklin', last_name='benjamin', email='lightningkeys@gmail.com', is_staff=True)
        admin.set_password('foo')
        admin.save()
        self.admin = admin

        project = Project(
                name='foo',
                team_dynamix_id=1,
                description='this is a project',
                created_by=self.admin,
                )
        project.save()
        self.project = project

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
                )
        ticket.save()
        self.ticket = ticket
