"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import random as r
import time, datetime

from django.test import TestCase 
from django.contrib.auth.models import User, Group, Permission
from django.utils.timezone import utc

from django_dynamic_fixture import G

from ..tickets.models import Ticket, Work


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TimesheetTest(TestCase):

    ticket_titles = ("Need additional text marquee on header and footer.", \
                     "Not enough frames on the main page.", \
                     "Google Maps not working in Netscape 4.0. Fix it.", \
                     "Flash doesn't work. Need more pizzazz.",
                     "Please add the thing to that page with the thingy.", \
                     "I don't know what I'm doing. Need help ASAP.", \
                     "Instructions unclear. I ordered a Pikachu in a blender.")
    
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

        self.end_date = datetime.datetime.now()
        #self.start_date = self.end_date - datetime.timedelta(hours=randint(1,7))
        #print "Start: %s vs. %s" % (self.start_date, self.end_date)

        self.create_tickets()

        self.client.login(username='jdoe', password='12345')

    def create_tickets(self):
        # This ticket+work is within the date range
        self.inrange_ticket = G(Ticket, title="In range", assigned_to=self.admin)
        end = self.end_date - datetime.timedelta(days=20)
        end = end.replace(tzinfo=utc)
        start = end - datetime.timedelta(hours=r.randint(1,7))
        start = start.replace(tzinfo=utc)
        self.inrange_work = G(Work, ticket=self.inrange_ticket, \
                 started_on=start, \
                 done_on=end, \
                 state=Work.DONE)
        # Create some random tickets+work
        for i in range(5):
            ticket = G(Ticket, title=r.choice(self.ticket_titles), assigned_to=self.admin)
            for j in range(r.randint(1,4)):
                end = self.end_date - datetime.timedelta(days=r.randint(0,40))
                end = end.replace(tzinfo=utc)
                start = end - datetime.timedelta(hours=r.randint(1,7))
                start = start.replace(tzinfo=utc)
                #print "Start: %s vs. End: %s" % (start, end)          
                work = G(Work, ticket=ticket, \
                         started_on=start, \
                         done_on=end, \
                         state=Work.DONE)
                work.save()
            ticket.save()

        # This ticket is out of the date range
        end = self.end_date - datetime.timedelta(days=60)
        end = end.replace(tzinfo=utc)
        start = end - datetime.timedelta(days=40)
        start = start.replace(tzinfo=utc)
        self.outofrange_ticket = G(Ticket, title="Out of range", assigned_to=self.admin)
        self.outofrange_work = G(Work, ticket=self.outofrange_ticket, \
                 started_on=start, \
                 done_on=end, \
                 state=Work.DONE)

    def test_timesheet_url(self):
        """Checks the url works
        """
        response = self.client.get('/accounts/timesheet/')
        #print response
        self.assertEqual(response.status_code, 200)

    def test_timesheet_range(self):
        """Checks only tickets & work in the specified date range appear
        """
        response = self.client.get('/accounts/timesheet/')
        #print dir(response.content)
        self.assertNotIn(u'#%s: %s' % (self.outofrange_ticket.pk, self.outofrange_ticket.title), response.content)
        self.assertIn(u'#%s: %s' % (self.inrange_ticket.pk, self.inrange_ticket.title), response.content)


