"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

from accounts.models import VerificationQueue

from emailusernames.utils import create_user, create_superuser

class SimpleTest(TestCase):

  def runTest(self):
    pass

  def setUp(self):
    """
      create usable accounts
    """
    ps_group, created = Group.objects.get_or_create(name="Party Specialist")
    ph_group, created = Group.objects.get_or_create(name="Party Host")
    att_group, created = Group.objects.get_or_create(name="Attendee")
    supp_group, created = Group.objects.get_or_create(name="Supplier")
    if not User.objects.filter(email="specialist1@example.com").exists():
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

  def test_verification_code(self):
    u = User.objects.get(email="attendee9@example.com")
    vque = VerificationQueue(user=u, verification_code="12345")
    vque.save()

  def test_user_creation(self):

    response = self.client.get(reverse("sign_up", args=[0]))
    self.assertContains(response, "Party Specialist")

    response = self.client.get(reverse("sign_up", args=[1]))
    self.assertContains(response, "Party Host")

    response = self.client.get(reverse("sign_up", args=[2]))
    self.assertContains(response, "Attendee")

    response = self.client.get(reverse("sign_up", args=[3]))
    self.assertContains(response, "Supplier")

    response = self.client.post(reverse("sign_up", args=[0]), {'first_name': 'John',
                                                                'last_name': 'Doe1',
                                                                'email': 'john.doe1@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up'})

    self.assertContains(response, "Verification Sent")

    response = self.client.post(reverse("sign_up", args=[0]), {'first_name': 'John',
                                                                'last_name': 'Doe2',
                                                                'email': 'john.doe1@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up'})
    self.assertContains(response, "A user with that email already exists")

    response = self.client.post(reverse("sign_up", args=[1]), {'first_name': 'John',
                                                                'last_name': 'Doe2',
                                                                'email': 'john.doe2@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up'})
    self.assertContains(response, "Verification Sent")

    # verify user
    temp_password = response.context['temp_password']
    verification_code = response.context['verification_code']

    response = self.client.get(reverse("verify_account", args=[verification_code]))
    self.assertEqual(response.status_code, 200)

    response = self.client.post(reverse("verify_account", args=[verification_code]), {
                                                                          'email': 'john.doe2@example.com',
                                                                          'temp_password': temp_password,
                                                                          'new_password': 'hello',
                                                                          'retype_password': 'hello1'})
    self.assertContains(response, "The new passwords do not match") 

    response = self.client.post(reverse("verify_account", args=[verification_code]), {
                                                                          'email': 'john.doe2@example.com',
                                                                          'temp_password': temp_password+"1",
                                                                          'new_password': 'hello',
                                                                          'retype_password': 'hello'})
    self.assertContains(response, "Your temporary password does not match") 

    response = self.client.post(reverse("verify_account", args=[verification_code]), {
                                                                          'email': 'john.doe3@example.com',
                                                                          'temp_password': temp_password+"1",
                                                                          'new_password': 'hello',
                                                                          'retype_password': 'hello1'})
    self.assertContains(response, "You should sign up first") 

    response = self.client.post(reverse("verify_account", args=[verification_code]), {
                                                                          'email': 'john.doe2@example.com',
                                                                          'temp_password': temp_password,
                                                                          'new_password': 'hello',
                                                                          'retype_password': 'hello'})
    self.assertRedirects(response, reverse("home_page"))

    verify = VerificationQueue.objects.get(verification_code=verification_code)
    user = User.objects.get(email='john.doe2@example.com')
    self.assertEquals(verify.verified, True)
    self.assertEquals(user.is_active, True)

    # create a supplier
    response = self.client.post(reverse("sign_up", args=[2]), {'first_name': 'John',
                                                                'last_name': 'Doe3',
                                                                'email': 'john.doe3@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up'})
    self.assertContains(response, "Verification Sent")

  def test_basic_addition(self):
    """
    Tests that 1 + 1 always equals 2.
    """
    self.assertEqual(1 + 1, 2)
