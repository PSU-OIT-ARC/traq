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
from .forms import TicketForm, WorkForm, CommentForm, BulkForm
from ..utils.tests import TraqCustomTest
from traq.projects.models import Project, Component, Milestone
from traq.tickets.models import Ticket, TicketType, TicketStatus, TicketPriority, Work, WorkType, Comment
from traq.todos.models import ToDo


class TicketModelsTest(TraqCustomTest):
    """
    Run through all the models to make sure they save correctly
    """
    def setUp(self):
        super(TicketModelsTest, self).setUp()

    def test_ticket_status_model(self):
        t = TicketStatus(
            name='Open',
            rank=1,
            is_default=True,
            importance=1,
        )
        t.save()
        self.assertEqual(str(t), 'Open')

    def test_ticket_model(self):
        t = Ticket(
            title='Test Ticket',
            body='Test ticket body',
            created_on=datetime.now(),
            started_on=datetime.now(),
            edited_on=datetime.now(),
            estimated_time= '01:00:00',
            is_deleted=False,
            is_extra=False,
            due_on=datetime.now(),
            is_internal=False,
            release='Test',
            branch='Test',
            created_by=self.admin,
            assigned_to=self.user,
            status=TicketStatus.objects.first(),
            priority=TicketPriority.objects.first(),
            project=Project.objects.first(),
            component=Component.objects.first(),
            milestone=Milestone.objects.first(),
            type=TicketType.objects.first(),
        )
        t.save()
        self.assertTrue(t.isOverDue)
        self.assertEqual(t.finishWork(), False)

    def test_ticket_type_model(self):
        t = TicketType(
            name='Test Ticket Type',
            description='Not to be confused with any other ticket type',
        )
        t.save()
        self.assertEqual(str(t), 'Test Ticket Type')

    def test_ticket_priority_model(self):
        t = TicketPriority(
            name='Open',
            rank=1,
            is_default=True,
        )
        t.save()
        self.assertEqual(str(t), 'Open')

    def test_work_model(self):
        w = Work(
            created_on=datetime.now(),
            description='Description of work',
            billable=True,
            time='10:00:00',
            started_on=pytz.UTC.localize(datetime.now()),
            done_on=pytz.UTC.localize(datetime.now()),
            state_changed_on=pytz.UTC.localize(datetime.now()),
            type=WorkType.objects.first(),
            ticket=Ticket.objects.first(),
            created_by=self.admin,
            is_deleted=False
        )
        w.save()
        w.continue_()
        w.done()
        self.assertEqual(w.duration(), '10:00:00')

    def test_work_type_model(self):
        w = WorkType(
            name='Test Work Type',
            price=10,
            is_default=True,
            rank=1,
        )
        w.save()
        self.assertEqual(str(w), 'Test Work Type')

    def test_comment_model(self):
        c = Comment(
            body='Test comment body',
            created_on=datetime.now(),
            edited_on=datetime.now(),
            is_deleted=False,
            todo=self.todo,
            created_by=self.admin,
        )
        c.cc={self.admin,}
        c.save()
        self.assertEqual(c.body, 'Test comment body')


class TicketFormsTest(TraqCustomTest):
    """
    Run through all the forms in the tickets app and make sure they work.
    """

    def setUp(self):
        super(TicketFormsTest, self).setUp()

    def test_invalid_ticket_form(self):
        f = TicketForm(project=self.project, user=self.user)
        self.assertFalse(f.is_valid())
        
    def test_valid_ticket_form(self):
        f = TicketForm(instance=None, project=self.project, user=self.admin, todo=self.todo, data={
            'title': 'Test',
            'body': 'testing body',
            'estimated_time': '10:00:00',
            'is_deleted': False,
            'created_by': self.user,
            'status': self.ticket.status.pk,
            'type': 1,
            'component': Component.objects.first().pk,
            'started_on': datetime.now(),
            'priority': 1,
        })
        self.assertTrue(f.is_valid())
        count = Ticket.objects.count()
        f.save()
        self.assertEqual(count+1, Ticket.objects.count())

    def test_comment_form(self):
        c = CommentForm(instance=None, 
            created_by=self.admin, 
            ticket=self.ticket, 
            data={
                'cc': [self.admin.pk,], 
                'body': 'test body',
                'is_deleted': False,
            }
        )
        self.assertTrue(c.is_valid())
        count = Comment.objects.count()
        c.save()
        self.assertEqual(count+1, Comment.objects.count())

    def test_work_form(self):
        w = WorkForm(instance=None,
            user=self.admin,
            ticket=self.ticket,
            data={
                'description': 'desc',
                'billable': True,
                'time': '10:10:00',
                'started_on': datetime.now(),
                'type': WorkType.objects.first().pk,
                'is_deleted': False,
            },
        )
        self.assertTrue(w.is_valid())
        count = Work.objects.count()
        w.save()
        self.assertEqual(count+1, Work.objects.count())

    def test_bulk_form(self):
        b = BulkForm(
            project=self.project,
            data={
                'priority': 1,
                'status':1,
                'assigned_to': self.admin.pk,
                'component': Component.objects.first().pk,
            }
        )
        self.assertTrue(b.is_valid())


class TicketDetailTest(TraqCustomTest):
    
    def setUp(self):
        super(TicketDetailTest, self).setUp()
        required_permissions = Permission.objects.get(codename='add_todo')
        self.admin.user_permissions.add(required_permissions)
        self.user.user_permissions.add(required_permissions)

    def test_get(self):
        self.logged_in = self.client.login(username='moltres', password='foo')
        response = self.client.get(reverse('tickets-detail', args=[self.ticket.pk]))
        self.assertEqual('tickets/detail.html', response.templates[0].name)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.logged_in = self.client.login(username='moltres', password='foo')
        response = self.client.post(reverse('tickets-detail', args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 200)

    def test_get_with_todos(self):
        self.client.logout()
        self.logged_in = self.client.login(username='raygun', password='foo')
        self.ticket.todos.add(self.todo)
        response = self.client.get(reverse('tickets-detail', args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 302)

    def test_post_with_junk_data(self):
        self.logged_in = self.client.login(username='moltres', password='foo')

        form = WorkForm(ticket=self.ticket, user=self.admin)
        data = {'form': form, 'form_type':'work_form',}

        self.assertFalse(form.is_valid())
        response = self.client.post(reverse('tickets-detail', args=[self.ticket.pk]), data)
        self.assertEqual(response.status_code, 200)

    def test_post_with_valid_data(self):
        self.logged_in = self.client.login(username='moltres', password='foo')
        data = {
                'description': 'this is a test',
                'time': '00:30:00',
                'type': 1,
                "form_type": "work_form",
                }
        response = self.client.post(reverse('tickets-detail', args=[self.ticket.pk]), data)
        self.assertRedirects(response, reverse("tickets-detail", args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 302)

        data = {
                'body': 'this is a comment',
                'form_type': 'comment_form',
                }
        response = self.client.post(reverse('tickets-detail', args=[self.ticket.pk]), data)
        self.assertEqual(response.status_code, 302)

class TicketCreateTest(TraqCustomTest):
    def setUp(self):
        super(TicketCreateTest, self).setUp()
        required_permissions = Permission.objects.get(codename='add_ticket')
        self.admin.user_permissions.add(required_permissions)
        self.user.user_permissions.add(required_permissions)
        self.logged_in = self.client.login(username='moltres', password='foo')

    def test_get(self):
        response = self.client.get(reverse('tickets-create', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_post_with_invalid_data(self):
        response = self.client.post(reverse('tickets-create', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_post_with_valid_data(self):
        data =  {
                'title': 'Peas',
                'body': 'Random body that is telling you what to do',
                'started_on': datetime.now(),
                'estimated_time': '01:00:00',
                'status': TicketStatus.objects.first().pk,
                'priority': 1,
                'created_by': self.admin.pk,            # I know it's gross looking but it took 
                'component': self.component.pk,         # an absurdly long time to get this to
                'project': self.project.pk,             # validate for some reason so just pretend
                'type': TicketType.objects.first().pk,  # you have beer goggles, and this code looks
                'todo': self.todo.pk,                   # like a ten.
                }
        response = self.client.post(reverse('tickets-create', args=[self.project.pk]), data)
        self.assertEqual(response.status_code, 302)


class TicketBulkTest(TraqCustomTest):
    def setUp(self):
        super(TicketBulkTest, self).setUp()
        required_permissions = Permission.objects.get(codename='change_ticket')
        self.admin.user_permissions.add(required_permissions)
        self.logged_in = self.client.login(username='moltres', password='foo')

    def test_get(self):
        response = self.client.get(reverse('tickets-bulk', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_invalid_post(self):
        with mock.patch('traq.tickets.forms.BulkForm.is_valid', return_value=False) as data:
            response = self.client.post(reverse('tickets-bulk', args=[self.project.pk,]), data=data)
        self.assertEqual(response.status_code, 200)

    def test_valid_post(self):
        with mock.patch('traq.tickets.models.Ticket'):
            with mock.patch('traq.tickets.forms.BulkForm.bulkUpdate', return_value=True):
                with mock.patch('traq.tickets.forms.BulkForm.is_valid', return_value=True) as data:
                    response = self.client.post(reverse('tickets-bulk', args=[self.project.pk,]), data=data)
        self.assertEqual(response.status_code, 302)


class TicketEditTest(TraqCustomTest):
    def setUp(self):
        super(TicketEditTest, self).setUp()
        required_permissions = Permission.objects.get(codename='change_ticket')
        self.admin.user_permissions.add(required_permissions)
        self.logged_in = self.client.login(username='moltres', password='foo')

    def test_get(self):
        response = self.client.get(reverse('tickets-edit', args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 200)

    def test_invalid_post(self):
        with mock.patch('traq.tickets.forms.TicketForm.is_valid', return_value=False) as form:
            response = self.client.post(reverse('tickets-edit', args=[self.ticket.pk]), data=form)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(ValidationError)

    def test_valid_post(self):
        with mock.patch('traq.tickets.forms.TicketForm.save', return_value=True):
            with mock.patch('traq.tickets.forms.TicketForm.is_valid', return_value=True) as data:
                response = self.client.post(reverse('tickets-edit', args=[self.ticket.pk]), data=data)
        self.assertEqual(response.status_code, 302)

class TicketListingTest(TraqCustomTest):
    def setUp(self):
        super(TicketListingTest, self).setUp()
        required_permissions = Permission.objects.get(codename='add_ticket')
        self.admin.user_permissions.add(required_permissions)
        self.logged_in = self.client.login(username='moltres', password='foo')

    def test_get(self):
        response = self.client.get(reverse('tickets-list', args=[self.project.pk,]))
        self.assertEqual(response.status_code, 200)


class CommentEditTest(TraqCustomTest):
    def setUp(self):
        super(CommentEditTest, self).setUp()
        required_permissions = Permission.objects.get(codename='change_comment')
        self.admin.user_permissions.add(required_permissions)
        self.logged_in = self.client.login(username='moltres', password='foo')

    def test_get(self):
        with mock.patch('django.core.urlresolvers.reverse', return_value=True):
            with mock.patch('traq.tickets.models.Comment.sendNotification', return_value=True):
                comment = make('Comment')
                with mock.patch('traq.tickets.models.Comment.todo'):
                    response = self.client.get(reverse('comments-edit', args=[comment.pk]))
        self.assertEqual(response.status_code, 200)

    def test_invalid_post(self):
        with mock.patch('django.core.urlresolvers.reverse', return_value=True):
            with mock.patch('traq.tickets.models.Comment.sendNotification', return_value=True):
                comment = make('Comment', todo=self.todo)
                with mock.patch('traq.tickets.forms.CommentForm.is_valid', return_value=True) as data:
                    with mock.patch('traq.tickets.forms.CommentForm.save', return_value=True):
                        response = self.client.post(reverse('comments-edit', args=[comment.pk]), data=data)
        self.assertEqual(response.status_code, 302)

from traq.projects.models import Project, Component
