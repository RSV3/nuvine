"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from main.models import ContactReason, ContactRequest
import random

class SimpleTest(TestCase):
  
  def runTest(self):
    pass

  def setUp(self):
    # initial data
    reason = ContactReason(reason="Interested in holding a party")
    reason.save()
    reason = ContactReason(reason="Interested in becoming a party specialist")
    reason.save()
    reason = ContactReason(reason="Interested in attending a party in my local area")
    reason.save()
    reason = ContactReason(reason="Interested in finding more about Winedora")
    reason.save()
    reason = ContactReason(reason="Send me any new updates")
    reason.save()
    reason = ContactReason(reason="Other")
    reason.save()

  def test_contact_us_models(self):
    total_reasons = ContactReason.objects.all().count()

    rand_ind = random.randint(1, total_reasons)
    reason = ContactReason.objects.get(id=rand_ind)
    req = ContactRequest(subject=reason, first_name="abc", last_name="def", email="hello@mit.edu", message="", zipcode="02139")
    req.save()

    rand_ind = random.randint(1, total_reasons)
    reason = ContactReason.objects.get(id=rand_ind)
    req = ContactRequest(subject=reason, first_name="abc", last_name="def", email="hello2@mit.edu", message="", zipcode="02139")
    req.save()

    rand_ind = random.randint(1, total_reasons)
    reason = ContactReason.objects.get(id=rand_ind)
    req = ContactRequest(subject=reason, first_name="abc", last_name="def", email="hello3@mit.edu", message="", zipcode="02139")
    req.save()


    rand_ind = random.randint(1, total_reasons)
    reason = ContactReason.objects.get(id=rand_ind)
    req = ContactRequest(subject=reason, first_name="abc", last_name="def", email="hello4@mit.edu", zipcode="02139")
    req.save()


  def test_basic_addition(self):
    """
    Tests that 1 + 1 always equals 2.
    """
    self.assertEqual(1 + 1, 2)
