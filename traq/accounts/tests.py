"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase 
from django.contrib.auth.models import User, Group, Permission

from django_dynamic_fixture import G

from ..tickets.models import Ticket


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TimesheetTest(TestCase):
    
    def setUp(self):
        super(TimesheetTest, self).setUp()
        perm = Permission.objects.get(codename='can_view_all')
        arc_group = Group(name='arc')
        arc_group.save()
        self.arc_group = arc_group

        admin = User(username='jdoe', first_name='Jane', last_name='Doe', email='jdoe@foo.com')
        admin.set_password('12345')    
        admin.save()
        admin.groups.add(arc_group)
        admin.user_permissions.add(perm)
        self.admin = admin

        self.client.login(username='jdoe', password='12345')


    def test_timesheet_url(self):
        response = self.client.get('/accounts/timesheet/')
        #print response
        self.assertEqual(response.status_code, 200)