"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

from accounts.models import VerificationQueue
from main.models import MyHost, ProSignupLog
from support.models import Email
from emailusernames.utils import create_user, create_superuser

from cms.tests import SimpleTest as CMSTest

class SimpleTest(TestCase):

  def runTest(self):
    pass

  def setUp(self):
    """
      create usable accounts
    """
    ps_group, created = Group.objects.get_or_create(name="Vinely Pro")
    ph_group, created = Group.objects.get_or_create(name="Vinely Host")
    att_group, created = Group.objects.get_or_create(name="Vinely Taster")
    supp_group, created = Group.objects.get_or_create(name="Supplier")
    pending_pro_group, created = Group.objects.get_or_create(name="Pending Vinely Pro")

    if not User.objects.filter(email="specialist1@example.com").exists():
      u = create_user("specialist1@example.com", "hello")
      u.groups.add(ps_group)
      u.is_staff = True
      u.save()

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

    test = CMSTest()
    test.create_all_templates()

  def test_verification_code(self):
    u = User.objects.get(email="attendee9@example.com")
    vque = VerificationQueue(user=u, verification_code="12345")
    vque.save()

  def test_user_creation(self):

    response = self.client.get(reverse("sign_up", args=[1]))
    self.assertContains(response, "Vinely Pro")

    response = self.client.get(reverse("sign_up", args=[2]))
    self.assertContains(response, "Vinely Host")

    response = self.client.get(reverse("sign_up", args=[3]))
    self.assertContains(response, "future Vinely party")

    # suppliers currently cannot sign up
    response = self.client.get(reverse("sign_up", args=[4]))
    self.assertEqual(response.status_code, 404)
    # self.assertContains(response, "Supplier")

    response = self.client.post(reverse("sign_up", args=[1]), {'first_name': 'John',
                                                                'last_name': 'Doe1',
                                                                'email': 'john.doe1@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up',
                                                                'zipcode': '49546'})
    self.assertContains(response, "Thank you for your interest in becoming a Vinely Pro")

    self.assertTrue(ProSignupLog.objects.filter(new_pro__email='john.doe1@example.com', mentor=None).exists())

    # check that emails are sent to vinely
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com', 'getstarted@vinely.com']", subject="Vinely Pro Request")
    self.assertTrue(vinely_recipients.exists())

    # check that emails are sent to recipient
    user_recipient = Email.objects.filter(recipients="[u'john.doe1@example.com']", subject="Vinely Pro Request!")
    self.assertTrue(user_recipient.exists())

    response = self.client.post(reverse("sign_up", args=[1]), {'first_name': 'John',
                                                                'last_name': 'Doe2',
                                                                'email': 'john.doe1@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up',
                                                                'zipcode': '49546'})
    self.assertContains(response, "A user with that email already exists")

    response = self.client.post(reverse("sign_up", args=[1]), {'first_name': 'John',
                                                                'last_name': 'Doe2',
                                                                'email': 'john.doe2@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up',
                                                                'zipcode': '49546',
                                                                'mentor': 'specialist1@example.com'})
    self.assertContains(response, "Thank you for your interest in becoming a Vinely Pro")

    # pro fake mentor email specified
    response = self.client.post(reverse("sign_up", args=[1]), {'first_name': 'John',
                                                                'last_name': 'Doe3',
                                                                'email': 'john.doe3@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up',
                                                                'zipcode': '49546',
                                                                'mentor': 'no.pro@example.com'})
    self.assertContains(response, "The mentor you specified is not a Vinely Pro")    

    # TODO: check zipcode is supported
    response = self.client.post(reverse("sign_up", args=[2]), {'first_name': 'John',
                                                                'last_name': 'Doe4',
                                                                'email': 'john.doe4@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up',
                                                                'zipcode': '49546',
                                                                'mentor': 'no.pro@example.com'})
    self.assertContains(response, "The Pro email you specified is not for a Vinley Pro")

    response = self.client.post(reverse("sign_up", args=[2]), {'first_name': 'John',
                                                                'last_name': 'Doe4',
                                                                'email': 'john.doe4@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up',
                                                                'zipcode': '49546',
                                                                'mentor': 'specialist1@example.com'})
    self.assertContains(response, "Thank you for your interest in hosting a Vinely Party!")
    
    self.assertTrue(MyHost.objects.filter(pro__email='specialist1@example.com', host__email='john.doe3@example.com').exists)

    # check that emails are sent to vinely + pro
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com', u'specialist1@example.com']", subject='A Vinely Taste Party is ready to be scheduled')
    self.assertTrue(vinely_recipients.exists())

    # check that emails are sent to recipient
    host_recipient = Email.objects.filter(recipients="[u'john.doe4@example.com']", subject='Get the party started with Vinely')
    self.assertTrue(host_recipient.exists())

    # host no pro specified
    response = self.client.post(reverse("sign_up", args=[2]), {'first_name': 'John',
                                                                'last_name': 'Doe5',
                                                                'email': 'john.doe5@example.com',
                                                                'password1': 'Sign Up',
                                                                'password2': 'Sign Up',
                                                                'zipcode': '49546'})
    self.assertContains(response, "Thank you for your interest in hosting a Vinely Party!")
    self.assertTrue(MyHost.objects.filter(pro=None, host__email='john.doe4@example.com').exists)

    # check that emails are sent to vinely
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com']", subject='A Vinely Taste Party is ready to be scheduled')
    self.assertTrue(vinely_recipients.exists())

    # verify user
    temp_password = response.context['temp_password']
    verification_code = response.context['verification_code']

    response = self.client.get(reverse("verify_account", args=[verification_code]))
    self.assertEqual(response.status_code, 200)

    response = self.client.post(reverse("verify_account", args=[verification_code]), {
                                                                          'email': 'john.doe5@example.com',
                                                                          'temp_password': temp_password,
                                                                          'new_password': 'hello',
                                                                          'retype_password': 'hello1',
                                                                          'accepted_tos': True})
    self.assertContains(response, "The new passwords do not match") 

    response = self.client.post(reverse("verify_account", args=[verification_code]), {
                                                                          'email': 'john.doe5@example.com',
                                                                          'temp_password': temp_password+"1",
                                                                          'new_password': 'hello',
                                                                          'retype_password': 'hello',
                                                                          'accepted_tos': True})
    self.assertContains(response, "Your temporary password does not match") 

    response = self.client.post(reverse("verify_account", args=[verification_code]), {
                                                                          'email': 'john.doe3@example.com',
                                                                          'temp_password': temp_password+"1",
                                                                          'new_password': 'hello',
                                                                          'retype_password': 'hello1',
                                                                          'accepted_tos': True})
    self.assertContains(response, "You should sign up first") 

    response = self.client.post(reverse("verify_account", args=[verification_code]), {
                                                                          'email': 'john.doe5@example.com',
                                                                          'temp_password': temp_password,
                                                                          'new_password': 'hello',
                                                                          'retype_password': 'hello',
                                                                          'accepted_tos': True})

    # user logged in
    self.assertRedirects(response, reverse("home_page"))

    verify = VerificationQueue.objects.get(verification_code=verification_code)
    user = User.objects.get(email='john.doe5@example.com')
    self.assertEquals(verify.verified, True)
    self.assertEquals(user.is_active, True)

    self.client.logout()

    # logged in as taster, sign up to be host
    response = self.client.login(email="attendee1@example.com", password="hello")
    self.assertEquals(response, True)

    response = self.client.get(reverse("sign_up", args=[2]))
    self.assertEquals(response.status_code, 200)

    self.assertContains(response, "Thank you for your interest in hosting a Vinely Party!")

    # taster added to MyHost
    self.assertTrue(MyHost.objects.filter(pro=None, host__email='attendee1@example.com').exists)

    # check that emails are sent to vinely
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com']", subject='A Vinely Taste Party is ready to be scheduled')
    self.assertTrue(vinely_recipients.exists())

    # check that emails are sent to taster
    host_recipient = Email.objects.filter(recipients="[u'attendee1@example.com']", subject='Thanks for your interest in becoming a Vinely Host!')
    self.assertTrue(host_recipient.exists())    

    # existing member of Vinely signing up as attendee
    # NOTE: User cannot sign up at the moment
    # response = self.client.post(reverse("sign_up", args=[3]), {'first_name': 'John',
    #                                                             'last_name': 'Doe2',
    #                                                             'email': 'john.doe2@example.com',
    #                                                             'password1': 'Sign Up',
    #                                                             'password2': 'Sign Up'})

    # self.assertContains(response, "active member of Vinely")

    

    # create a supplier
    # NOTE: Supplier cannot sign up at the moment
    # response = self.client.post(reverse("sign_up", args=[4]), {'first_name': 'John',
    #                                                             'last_name': 'Doe4',
    #                                                             'email': 'john.doe4@example.com',
    #                                                             'password1': 'Sign Up',
    #                                                             'password2': 'Sign Up'})

    # self.assertContains(response, "e-mail to verify your e-mail address")

  def test_my_information_update(self):
    response = self.client.login(email="attendee2@example.com", password="hello")
    self.assertEquals(response, True)

    # modify only basic info
    response = self.client.get(reverse("my_information"))
    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("my_information"), {
                                                  'user-first_name': 'Jane',
                                                  'user-last_name': 'Doe', 
                                                  'user-email': 'attendee2@example.com'
                                                })

    self.assertContains(response, "Your information has been updated")

    # change e-mail address
    response = self.client.post(reverse("my_information"), {
                                                  'user-first_name': 'Jane',
                                                  'user-last_name': 'Doe', 
                                                  'user-email': 'john.doe@example.com'
                                                })

    self.assertContains(response, "Your information has been updated")

    response = self.client.post(reverse("my_information"), {
                                                  'profile-phone': '617-234-2524',
                                                  'user-last_name': 'Doe', 
                                                  'user-email': 'john.doe@example.com'
                                                })

    self.assertContains(response, "Your information has been updated")

    # modify only shipping
    response = self.client.post(reverse("my_information"), {
                                                  'shipping-street1': '55 Memorial Dr.',
                                                  'shipping-street2': '#14', 
                                                  'shipping-city': 'North Haven',
                                                  'shipping-state': 'CT',
                                                  'shipping-zipcode': '48105'
                                                })

    self.assertContains(response, "Your information has been updated")

    response = self.client.post(reverse("my_information"), {
                                                  'shipping-street1': '55 Memorial Dr.',
                                                  'shipping-city': 'North Haven',
                                                  'shipping-state': 'CT',
                                                  'shipping-zipcode': '48105'
                                                })

    self.assertContains(response, "Your information has been updated")
  
    # modify only billing
    response = self.client.post(reverse("my_information"), {
                                                  'billing-street1': '140 Columbia St.',
                                                  'billing-street2': '#2', 
                                                  'billing-city': 'Cambridge',
                                                  'billing-state': 'MA',
                                                  'billing-zipcode': '02139'
                                                })

    self.assertContains(response, "Your information has been updated")
  
    response = self.client.post(reverse("my_information"), {
                                                  'billing-street1': '140 Columbia St.',
                                                  'billing-city': 'Detroit',
                                                  'billing-state': 'MI',
                                                  'billing-zipcode': '48115'
                                                })

    self.assertContains(response, "Your information has been updated")

    response = self.client.post(reverse("my_information"), {
                                                  'billing-city': 'Detroit',
                                                  'billing-state': 'MI',
                                                  'billing-zipcode': '48115'
                                                })

    self.assertContains(response, "This field is required")   
  
    # modify only payment
    response = self.client.post(reverse("my_information"), {
                                                  'payment-card_type': 'Unknown',
                                                  'payment-card_number': '4111111111111111',
                                                  'payment-exp_month': '7', 
                                                  'payment-exp_year': '2013',
                                                  'payment-verification_code': '555',
                                                  'payment-billing_zipcode': '48105'
                                                })

    self.assertContains(response, "Your information has been updated")

    response = self.client.post(reverse("my_information"), {
                                                  'payment-card_number': '4111111111111111111',
                                                  'payment-exp_month': '8', 
                                                  'payment-exp_year': '2015',
                                                  'payment-billing_zipcode': '48105'
                                                })

    self.assertContains(response, "This field is required")


    response = self.client.post(reverse("my_information"), {
                                                  'payment-card_type': 'Visa',
                                                  'payment-card_number': '4111111111111111',
                                                  'payment-exp_month': '8', 
                                                  'payment-exp_year': '2015',
                                                  'payment-verification_code': '342',
                                                  'payment-billing_zipcode': '48105'
                                                })

    self.assertContains(response, "Your information has been updated")   

    print "Information update test all work"

  def test_basic_addition(self):
    """
    Tests that 1 + 1 always equals 2.
    """
    self.assertEqual(1 + 1, 2)
