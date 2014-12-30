"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from traq.utils.tests import TraqCustomTest
from traq.projects.models import Component, Milestone, Project 
from traq.tickets.models import Ticket, Work, TicketStatus, TicketPriority
from . import views

class AccountTest(TraqCustomTest):
    def setUp(self):
        super(AccountTest, self).setUp()
        logged_in = self.client.login(username='moltres', password='foo')

    def test_profile_tickets(self):
        response = self.client.get(reverse('accounts-profile'))
        self.assertEqual(response.status_code, 200)

