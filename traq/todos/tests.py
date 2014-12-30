"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import pytz
from unittest import TestCase, mock
from unittest.mock import patch
from datetime import datetime, timedelta
from model_mommy.mommy import make
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from traq.tickets.forms import TicketForm, WorkForm, CommentForm, BulkForm
from ..utils.tests import TraqCustomTest
from traq.projects.models import Project, Component, Milestone
from traq.tickets.models import Ticket, TicketType, TicketStatus, TicketPriority, Work, WorkType, Comment
from traq.todos.models import ToDo
from traq.todos.forms import ToDoForm


class TodoModelsTest(TraqCustomTest):
    def setUp(self):
        super(TodoModelsTest, self).setUp()

    def test_todo(self):
        t = ToDo(
            title="Todo title",
            body='todo body',
            created_on=datetime.now(),
            estimate=10,
            is_deleted=False,
            due_on=datetime.now(),
            status=TicketStatus.objects.first(),
            rank=1,
            project=self.project,
            created_by=self.admin,
            priority=TicketPriority.objects.first(),
            component=Component.objects.first(),
        )
        count = ToDo.objects.count()
        t.save()
        self.assertEqual(count+1, ToDo.objects.count())


class TodoFormsTest(TraqCustomTest):
    def setUp(self):
        super(TodoFormsTest, self).setUp()

    def test_invalid_todo_form(self):
        t = ToDoForm(project=self.project, user=self.user)
        self.assertFalse(t.is_valid())

    def test_valid_todo_form(self):
        t = ToDoForm(
            project=self.project, 
            user=self.user,
            data={
                'title':"Todo title",
                'body': "todo body",
                'started_on': datetime.now(),
                'estimate': 100,
                'is_deleted': False,
                'status': 1,
                'priority': 1,
                'component': Component.objects.first().pk,
                'due_on': datetime.now(),
            }
        )
        self.assertTrue(t.is_valid())
        count = ToDo.objects.count()
        t.save()
        self.assertEqual(count+1, ToDo.objects.count())


class TodoViewsTest(TraqCustomTest):
    def setUp(self):
        super(TodoViewsTest, self).setUp()
        required_permissions = Permission.objects.get(codename='add_todo')
        self.admin.user_permissions.add(required_permissions)
        required_permissions = Permission.objects.get(codename='can_view_all')
        self.admin.user_permissions.add(required_permissions)
        required_permissions = Permission.objects.get(codename='change_todo')
        self.admin.user_permissions.add(required_permissions)
        self.logged_in = self.client.login(username='moltres', password='foo')

    def test_listing_view(self):
        response = self.client.get(reverse('todos-list', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_create_view_get(self):
        response = self.client.get(reverse('todos-create', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_create_view_invalid_post(self):
        response = self.client.post(reverse('todos-create', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_create_view_valid_post(self):
        data={
            'title':"Todo title",
            'body': "todo body",
            'started_on': datetime.now(),
            'estimate': 100,
            'is_deleted': False,
            'status': 1,
            'priority': 1,
            'component': Component.objects.first().pk,
            'due_on': datetime.now(),
        }
        response = self.client.post(reverse('todos-create', args=[self.project.pk,]), data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_view_get(self):
        response = self.client.get(reverse('todos-detail', args=[self.todo.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_detail_view_post(self):
        with patch('traq.tickets.forms.CommentForm.is_valid', return_value=True):
            with patch('traq.tickets.forms.CommentForm.save', return_value=True):
                response = self.client.post(reverse('todos-detail', args=[self.todo.pk,]), data={"form_type":"comment_form",})
        self.assertEqual(response.status_code, 302)

    def test_edit_view_get(self):
        response = self.client.get(reverse('todos-edit', args=[self.todo.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_edit_view_invalid_post(self):
        response = self.client.post(reverse('todos-edit', args=[self.todo.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_edit_view_valid_post(self):
        with patch('traq.todos.forms.ToDoForm.is_valid', return_value=True):
            with patch('traq.todos.forms.ToDoForm.save', return_value=True):
                response = self.client.post(reverse('todos-edit', args=[self.todo.pk,]))
        self.assertEqual(response.status_code, 302)

    def test_prioritize_view_get(self):
        response = self.client.get(reverse('todos-prioritize', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_prioritize_view_post(self):
        data = {
            "pk": [self.todo.pk],
        }
        response = self.client.post(reverse('todos-prioritize', args=[self.project.pk,]), data=data)
        self.assertEqual(response.status_code, 200)

