"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import random as r
import time, datetime
import json
from unittest.mock import patch, Mock
from django.utils.timezone import now
from django.contrib.auth.models import User, Group, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import utc
from model_mommy.mommy import make
from traq.projects.models import Component, Milestone, Project
from traq.tickets.models import Ticket, Work, TicketStatus, TicketPriority
from traq.utils.tests import TraqCustomTest
from . import views

class AccountTest(TraqCustomTest):
    def setUp(self):
        super(AccountTest, self).setUp()
        logged_in = self.client.login(username='moltres', password='foo')

    def test_profile_tickets(self):
        response = self.client.get(reverse('accounts-profile'))
        self.assertEqual(response.status_code, 200)

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

# need to mockup the JSON that reddit returns
json_binary = json.dumps({
    "data": {
        "children": [
            {
                "data": {
                    "url": "http://b.thumbs.redditmedia.com/cbzTf1qlV61zh4RfdQNbWBe-cQFkytvrIHmYvEevc5I.jpg",
                    "thumbnail": "http://b.thumbs.redditmedia.com/cbzTf1qlV61zh4RfdQNbWBe-cQFkytvrIHmYvEevc5I.jpg?1"
                }
            }
        ]
    }
}).encode("utf8")
@patch("traq.templatetags.timesheet.urllib.request.urlopen", new=Mock(return_value=Mock(read=lambda: json_binary)))
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

        self.today = datetime.date.today()
        self.end_date = datetime.datetime(self.today.year, self.today.month+1, 15, tzinfo=utc)

        self.create_tickets()

        self.client.login(username='jdoe', password='12345')

    def create_tickets(self):
        # This ticket+work is within the date range
        self.inrange_ticket = make(Ticket, title="In range", assigned_to=self.admin)
        # the default interval for the timesheet is the 15th of the current
        # month, to the 16th of the previous month, so the end date of the work
        # must not be greater than 15 -- otherwise the tests will fail if they
        # run at the beginning of a month
        end = self.end_date - datetime.timedelta(days=5)
        delta = datetime.timedelta(hours=r.randint(1,7))
        start = end - delta

        self.inrange_work = make(Work, ticket=self.inrange_ticket, \
                 started_on=start, \
                 done_on=end, \
                 time=str(delta), \
                 state=Work.DONE)
        self.inrange_work.save()
        self.inrange_ticket.save()

        # Create some random tickets+work
        for i in range(5):
            ticket = make(Ticket, title=r.choice(self.ticket_titles), assigned_to=self.admin)
            for j in range(r.randint(1,4)):
                end = self.end_date - datetime.timedelta(days=r.randint(0,40))
                delta = datetime.timedelta(hours=r.randint(1,7))
                start = end - delta
                work = make(Work, ticket=ticket, \
                         started_on=start, \
                         done_on=end, \
                         time=str(delta), \
                         state=Work.DONE)
                work.save()
            ticket.save()

        # This ticket is out of the date range
        end = self.end_date - datetime.timedelta(days=60)
        delta = datetime.timedelta(hours=5)
        start = end - delta
        self.outofrange_ticket = make(Ticket, title="Out of range", assigned_to=self.admin)
        self.outofrange_work = make(Work, ticket=self.outofrange_ticket, \
                 started_on=start, \
                 done_on=end, \
                 time=str(delta), \
                 state=Work.DONE)
        self.outofrange_work.save()
        self.outofrange_ticket.save()

    def test_timesheet_url(self):
        """Checks the url works
        """
        response = self.client.get('/accounts/timesheet/')
        self.assertEqual(response.status_code, 200)

    def test_timesheet_range(self):
        """Checks only tickets & work in the specified date range appear
        """
        response_get = self.client.get('/accounts/timesheet/')
        response = response_get.content.decode()

        if self.today.day < 16:
            self.assertIn(u'%s-%s-16' % (self.today.year, '{:02d}'.format(self.today.month-1)), response)
            self.assertIn(u'%s-%s-15' % (self.today.year, '{:02d}'.format(self.today.month)), response)
        else:
            self.assertIn(u'%s-%s-16' % (self.today.year, '{:02d}'.format(self.today.month)), response)
            self.assertIn(u'%s-%s-15' % (self.today.year, '{:02d}'.format(self.today.month+1)), response)

        self.assertNotIn(u'#%s: %s' % (self.outofrange_ticket.pk, self.outofrange_ticket.title), response)

        #self.assertIn(u'#%s: %s' % (self.inrange_ticket.pk, self.inrange_ticket.title), response)
