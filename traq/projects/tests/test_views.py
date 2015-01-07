"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from unittest import mock
from unittest.mock import patch
from datetime import datetime
from django.utils.timezone import now
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase
from traq.tickets.models import Ticket, TicketStatus, TicketPriority
from traq.projects.models import Project, Component, Milestone
from traq.projects.forms import ProjectForm, ComponentForm, MilestoneForm, ReportIntervalForm, ReportFilterForm, ProjectSprintForm
from traq.utils.tests import TraqCustomTest

class ProjectInitViewsTest(TraqCustomTest):
    def setUp(self):
        super(ProjectInitViewsTest, self).setUp()
        perm = Permission.objects.get(codename='can_view_all') 
        self.admin.user_permissions.add(perm)
        self.client.login(username='moltres', password='foo')

    def test_all(self):
        response = self.client.get(reverse('projects-all'))
        self.assertEqual(response.status_code, 200)

    def test_meta(self):
        project = self.project.pk
        response = self.client.get(reverse('projects-meta', args=[project,]))
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        project = self.project.pk
        response = self.client.get(reverse('projects-detail', args=[project,]))
        self.assertEqual(response.status_code, 200)

    def test_edit_get(self):
        perm = Permission.objects.get(codename='change_project')
        self.admin.user_permissions.add(perm)
        project = self.project.pk
        response = self.client.get(reverse('projects-edit', args=[project,]))
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        perm = Permission.objects.get(codename='change_project')
        self.admin.user_permissions.add(perm)
        project = self.project.pk
        with patch('traq.projects.forms.ProjectForm.is_valid', return_value=True) as data:
            with patch('traq.projects.forms.ProjectForm.save', return_value=True):
                response = self.client.post(reverse('projects-edit', args=[project,]), data=data)
        self.assertRedirects(response, reverse('projects-all'))

    def test_create_get(self):
        perm = Permission.objects.get(codename='add_project')
        self.admin.user_permissions.add(perm)
        response = self.client.get(reverse('projects-create'))
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        perm = Permission.objects.get(codename='add_project')
        self.admin.user_permissions.add(perm)
        with patch('traq.projects.forms.ProjectForm.is_valid', return_value=True) as data:
            with patch('traq.projects.forms.ProjectForm.save', return_value=True):
                with patch('traq.projects.models.Project.createDefaultComponents', return_value=True):
                    response = self.client.post(reverse('projects-create'), data=data)
        self.assertRedirects(response, reverse('projects-all'))

    def test_search(self):
        response = self.client.get(reverse('projects-search', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_edit_sprint_get(self):
        perm = Permission.objects.get(codename='change_project')
        self.admin.user_permissions.add(perm)
        response = self.client.get(reverse('projects-edit-sprint', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_edit_sprint_post(self):
        perm = Permission.objects.get(codename='change_project')
        self.admin.user_permissions.add(perm)
        with patch('traq.projects.forms.ProjectSprintForm.is_valid', return_value=True):
            response = self.client.post(reverse('projects-edit-sprint', args=[self.project.pk,]))
        self.assertRedirects(response, reverse('projects-detail', args=[self.project.pk]))


class ProjectComponentsViewsTest(TraqCustomTest):
    def setUp(self):
        super(ProjectComponentsViewsTest, self).setUp()
        perm = Permission.objects.get(codename='add_component') 
        self.admin.user_permissions.add(perm)
        self.client.login(username='moltres', password='foo')

    def test_create_get(self):
        response = self.client.get(reverse('components-create', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        with patch('traq.projects.forms.ComponentForm.is_valid', return_value=True) as data:
            with patch('traq.projects.forms.ComponentForm.save', return_value=True):
                response = self.client.post(reverse('components-create', args=[self.project.pk,]), data=data)
        self.assertEqual(response.status_code, 302)

    def test_edit_get(self):
        self.component = Component.objects.create(name='component', created_by=self.admin, rank=1, invoice_description='invoice', is_default=True, is_deleted=False, project=self.project)
        perm = Permission.objects.get(codename='change_component') 
        self.admin.user_permissions.add(perm)
        response = self.client.get(reverse('components-edit', args=[self.component.pk]))
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        self.component = Component.objects.create(name='component', created_by=self.admin, rank=1, invoice_description='invoice', is_default=True, is_deleted=False, project=self.project)
        perm = Permission.objects.get(codename='change_component') 
        self.admin.user_permissions.add(perm)
        with patch('traq.projects.forms.ComponentForm.is_valid', return_value=True) as data:
            with patch('traq.projects.forms.ComponentForm.save', return_value=True):
                response = self.client.post(reverse('components-edit', args=[self.component.pk,]), data=data)
        self.assertEqual(response.status_code, 302)

class ProjectsMilestonesViewsTest(TraqCustomTest):
    def setUp(self):
        super(ProjectsMilestonesViewsTest, self).setUp()
        self.milestone = Milestone.objects.create(due_on=now(), created_by=self.admin, project=self.project)
        perm = Permission.objects.get(codename='can_view_all') 
        self.admin.user_permissions.add(perm)
        self.client.login(username='moltres', password='foo')

    def test_create_get(self):
        perm = Permission.objects.get(codename='add_milestone') 
        self.admin.user_permissions.add(perm)
        response = self.client.get(reverse('milestones-create', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        perm = Permission.objects.get(codename='add_milestone') 
        self.admin.user_permissions.add(perm)
        with patch('traq.projects.forms.MilestoneForm.is_valid', return_value=True) as data:
            with patch('traq.projects.forms.MilestoneForm.save', return_value=True):
                response = self.client.post(reverse('milestones-create', args=[self.project.pk,]), data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail(self):
        perm = Permission.objects.get(codename='can_view_all') 
        self.admin.user_permissions.add(perm)
        response = self.client.get(reverse('milestones-detail', args=[self.milestone.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_edit_get(self):
        perm = Permission.objects.get(codename='change_milestone') 
        self.admin.user_permissions.add(perm)
        response = self.client.get(reverse('milestones-edit', args=[self.milestone.pk,]))
        self.assertTrue(response.status_code, 200)

    def test_edit_post(self):
        perm = Permission.objects.get(codename='change_milestone') 
        self.admin.user_permissions.add(perm)
        with patch('traq.projects.forms.MilestoneForm.is_valid', return_value=True) as data:
            with patch('traq.projects.forms.MilestoneForm.save', return_value=True):
                response = self.client.post(reverse('milestones-edit', args=[self.milestone.pk,]))
        self.assertTrue(response.status_code, 302)

class ProjectReportViewsTest(TraqCustomTest):
    def setUp(self):
        super(ProjectReportViewsTest, self).setUp()
        perm = Permission.objects.get(codename='can_view_all') 
        self.admin.user_permissions.add(perm)
        self.client.login(username='moltres', password='foo')

    def test_mega_get(self):
        response = self.client.get(reverse('projects-reports-mega'))
        self.assertEqual(response.status_code, 200)

    def test_grid_get(self):
        response = self.client.get(reverse('projects-reports-grid', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_summary(self):
        response = self.client.get(reverse('projects-reports-summary'))
        self.assertEqual(response.status_code, 200)

    def test_component(self):
        response = self.client.get(reverse('projects-reports-component', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_invoice(self):
        response = self.client.get(reverse('projects-reports-invoice', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

class ProjectScrumViewsTest(TraqCustomTest):
    def setUp(self):
        super(ProjectScrumViewsTest, self).setUp()
        perm = Permission.objects.get(codename='can_view_all') 
        self.admin.user_permissions.add(perm)
        self.client.login(username='moltres', password='foo')

    def test_dashboard(self):
        response = self.client.get(reverse('projects-dashboard', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_backlog(self):
        perm = Permission.objects.get(codename='change_todo') 
        self.admin.user_permissions.add(perm)
        with patch('traq.projects.models.Project.backlog', return_value=None):
            response = self.client.get(reverse('projects-backlog', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_sprint_planning(self):
        perm = Permission.objects.get(codename='change_todo') 
        self.admin.user_permissions.add(perm)
        response = self.client.get(reverse('projects-sprint-planning', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_scrum(self):
        response = self.client.get(reverse('projects-scrum', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

