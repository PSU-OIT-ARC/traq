"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from unittest import mock
from unittest.mock import patch
from datetime import datetime
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


