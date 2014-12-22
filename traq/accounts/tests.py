"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django_dynamic_fixture import G

from ..tickets.models import Ticket

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class TimesheetTest(TestCase):
	def test_ts_url(self):
		response = self.client.get('/accounts/profile/timesheet/')
		print response