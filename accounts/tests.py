"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group

from emailusernames.utils import create_user, create_superuser

class SimpleTest(TestCase):

  def runTest(self):
    pass

  def setUp(self):
    """
      create usable accounts
    """
    ps_group = Group.objects.create(name="Party Specialist")
    ph_group = Group.objects.create(name="Party Host")
    att_group = Group.objects.create(name="Attendee")
    supp_group = Group.objects.create(name="Supplier")
    u = create_user("specialist1@example.com", "hello")
    u.groups.add(ps_group)

    u = create_user("specialist2@example.com", "hello")
    u.groups.add(ps_group)

    u = create_user("host1@example.com", "hello")
    u.groups.add(ph_group)

    u = create_user("host2@example.com", "hello")
    u.groups.add(ph_group)

    u = create_user("host3@example.com", "hello")
    u.groups.add(ph_group)

    u = create_user("attendee1@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee2@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee3@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee4@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee5@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee6@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee7@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee8@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee9@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("supplier1@example.com", "hello")
    u.groups.add(supp_group)

    u = create_user("supplier2@example.com", "hello")
    u.groups.add(supp_group)

    suppliers = User.objects.filter(groups=supp_group)
    self.assertEqual(suppliers.count(), 2)

    attendees = User.objects.filter(groups=att_group)
    self.assertEqual(attendees.count(), 9)


  def test_basic_addition(self):
    """
    Tests that 1 + 1 always equals 2.
    """
    self.assertEqual(1 + 1, 2)
