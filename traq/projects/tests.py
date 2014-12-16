"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from traq.tickets.models import Ticket, TicketStatus, TicketPriority
from traq.projects.models import Project, Component


def create_users(self):
    user = User(username='raygun', first_name='bob', last_name='dole', email='bobdole@bobdole.com')
    user.set_password('foo')
    user.save()
    self.user = user

    admin = User(username='moltres', first_name='franklin', last_name='benjamin', email='lightningkeys@gmail.com', is_staff=True)
    admin.set_password('foo')
    admin.save()
    self.admin = admin

def create_projects(self):
    project = Project(
            name='foo',
            team_dynamix_id=1,
            description='this is a project',
            created_by=self.admin,
            )
    project.save()
    self.project = project
    return self.project # return so it can be called from within a constructor

def create_components(self):
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
    return self.component # return so it can be called from within a constructor

def create_tickets(self):
    ticket = Ticket(
            title='ticket', 
            body='body', 
            created_by=self.admin, 
            status=TicketStatus.objects.first(), 
            priority=TicketPriority.objects.first(), 
            project=create_projects(self),
            component=create_components(self),
            )
    ticket.save()
    self.ticket = ticket


class ReportTest(TestCase):
    def setUp(self):
        super(ReportTest, self).setUp()
        create_users(self)
        create_projects(self)
        create_components(self)
        create_tickets(self)
        self.client.login(email=self.admin.email, password='foo')

    def test_mega(self):
        result = self.client.get(reverse('projects-reports-mega'))
        self.assertEqual(result.status_code, 302)
