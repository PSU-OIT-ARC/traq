"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from traq.tickets.models import Ticket, TicketStatus, TicketPriority
from traq.projects.models import Project, Component, Milestone
from traq.projects.forms import ProjectForm, ComponentForm, MilestoneForm, ReportIntervalForm, ProjectSprintForm
from traq.utils.tests import TraqCustomTest


class ProjectModelsTest(TraqCustomTest):
    def setUp(self):
        super(ProjectModelsTest, self).setUp()

    def test_project_model(self):
        p = Project(
            name='Test Project',
            team_dynamix_id=111,
            description='hello, world',
            created_on=datetime.now(),
            is_deleted=False,
            pm_email=False,
            pm=self.user,
            status=1,
            point_of_contact='foobar',
            invoice_description='very descriptive',
            catch_all='everything',
            technical='holla back',
            created_by=self.admin,
            estimated_hours=20,
            is_scrum=False,
        )
        p.save()
        self.assertEqual(str(p), p.name)
        self.assertEqual(len(p.tickets()), 0)

    def test_component_model(self):
        c = Component(
            name='Test component',
            description='this is very descriptive',
            invoice_description='Wyatt go make me a sandwich',
            rank=1,
            is_default=True,
            is_deleted=False,
            project=self.project,
            created_by=self.admin,
        )
        c.save()
        self.assertEqual(str(c), c.name)

    def test_milestone_model(self):
        m = Milestone(
            created_on=datetime.now(),
            name='Test Milestone',
            due_on=datetime.now(),
            is_deleted=False,
            created_by=self.admin,
            project=self.project,
        )
        m.save()
        self.assertIn(m.name, str(m))


class ProjectFormsTest(TraqCustomTest):
    def setUp(self):
        super(ProjectFormsTest, self).setUp()

    def test_invalid_project_form(self):
        p = ProjectForm(created_by=self.admin)
        self.assertFalse(p.is_valid())

    def test_valid_project_form(self):
        p = ProjectForm(
            instance=None,
            created_by=self.admin,
            data={
                'name':'Test',
                'description':'testing out the description',
                'point_of_contact':'to hang out',
                'invoice_description':'describing the invoice',
                'catch_all':'the pokemon',
                'status':1,
                'is_deleted':False,
                'pm_email':False,
                'pm':self.admin.pk,
                'estimated_hours':10,
                'is_scrum':False,
                'target_completion_date':datetime.now(),
            }
        )
        self.assertTrue(p.is_valid())
        count = Project.objects.count()
        p.save()
        self.assertEqual(count+1, Project.objects.count())

    def test_invalid_component_form(self):
        c = ComponentForm(project=self.project, created_by=self.admin)
        self.assertFalse(c.is_valid())

    def test_valid_component_form(self):
        c = ComponentForm(project=self.project, created_by=self.admin, data={
        })
    

class ReportTest(TraqCustomTest):
    def setUp(self):
        super(ReportTest, self).setUp()

