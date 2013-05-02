"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from accounts.models import VerificationQueue, UserProfile
from main.models import ProSignupLog
from support.models import Email

from cms.tests import SimpleTest as CMSTest
from main.tests import SimpleTest as MainTest
from accounts.utils import get_default_pro


class SimpleTest(TestCase):

  def runTest(self):
    pass

  def setUp(self):
    """
      create usable accounts
    """
    test = CMSTest()
    test.create_all_templates()

    main_test = MainTest()
    main_test.create_usable_accounts()
    main_test.create_wine_personalities()
    main_test.create_wine_samplers()
    # main_test.create_products()

  def test_verification_code(self):
    u = User.objects.get(email="attendee9@example.com")
    vque = VerificationQueue(user=u, verification_code="12345")
    vque.save()

  def test_user_creation(self):
    # 1. Anonymous user signs up as Pro in anonymous
    response = self.client.post(reverse("make_pro", args=['signup']),  {'first_name': 'John',
                                                                        'last_name': 'Doe1',
                                                                        'email': 'john.doe1@example.com',
                                                                        'password1': 'Sign Up',
                                                                        'password2': 'Sign Up',
                                                                        'zipcode': '92612',
                                                                        'phone_number': '6172342524'})

    self.assertRedirects(response, reverse('home_page'))
    self.assertTrue(ProSignupLog.objects.filter(new_pro__email='john.doe1@example.com', mentor__email='elizabeth@vinely.com').exists())

    # test autoassign working --> Should assign default Pro
    profile = UserProfile.objects.get(user__email='john.doe1@example.com')
    # pro = User.objects.get(email='elizabeth@vinely.com')
    self.assertEquals(profile.mentor, get_default_pro())

    # check that emails are sent to vinely
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com', 'getstarted@vinely.com']", subject="Vinely Pro Request")
    self.assertTrue(vinely_recipients.exists())

    # check that emails are sent to recipient
    user_recipient = Email.objects.filter(recipients="[u'john.doe1@example.com']", subject="Vinely Pro Request!")
    self.assertTrue(user_recipient.exists())

    self.client.logout()

    # 2. Anonymous user signs up with email of existing user
    response = self.client.post(reverse("make_pro", args=['signup']),  {'first_name': 'John',
                                                                        'last_name': 'Doe2',
                                                                        'email': 'john.doe1@example.com',
                                                                        'password1': 'Sign Up',
                                                                        'password2': 'Sign Up',
                                                                        'zipcode': '92612',
                                                                        'phone_number': '6172342524'})
    self.assertContains(response, "A user with that email already exists")

    # 3. Existing taster signs up as Pro from account
    response = self.client.login(email="attendee1@example.com", password="hello")
    self.assertEquals(response, True)

    response = self.client.post(reverse("make_pro", args=['signup']),  {'first_name': 'One',
                                                                        'last_name': 'Attendee',
                                                                        'email': 'attendee1@example.com',
                                                                        'password1': 'Sign Up',
                                                                        'password2': 'Sign Up',
                                                                        'zipcode': '02139',
                                                                        'phone_number': '6172342524'})
    self.assertRedirects(response, reverse('home_page'))
    # check that emails are sent to vinely
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com', 'getstarted@vinely.com']", subject="Vinely Pro Request")
    self.assertTrue(vinely_recipients.exists())

    # check that emails are sent to recipient
    user_recipient = Email.objects.filter(recipients="[u'john.doe1@example.com']", subject="Vinely Pro Request!")
    self.assertTrue(user_recipient.exists())

    # test autoassign working --> Should assign MA Pro for zipcode used
    profile = UserProfile.objects.get(user__email='attendee1@example.com')
    # pro = User.objects.get(email='specialist1@example.com')
    self.assertEquals(profile.mentor, get_default_pro())

    self.client.logout()

    # 4. pro fake mentor email specified
    response = self.client.post(reverse("make_pro", args=['signup']),  {'first_name': 'John',
                                                                        'last_name': 'Doe3',
                                                                        'email': 'john.doe3@example.com',
                                                                        'password1': 'Sign Up',
                                                                        'password2': 'Sign Up',
                                                                        'zipcode': '92612',
                                                                        'phone_number': '6172342524',
                                                                        'mentor': 'no.pro@example.com'})

    self.assertContains(response, "The mentor you specified is not a Vinely Pro")
    self.client.logout()

    # TODO: check zipcode is supported
    # 5. Anonymous sign up as host - pro specified
    response = self.client.post(reverse("make_host", args=['signup']), {'first_name': 'John',
                                                                        'last_name': 'Doe4',
                                                                        'email': 'john.doe4@example.com',
                                                                        'password1': 'Sign Up',
                                                                        'password2': 'Sign Up',
                                                                        'zipcode': '92612',
                                                                        'phone_number': '6172342524',
                                                                        'mentor': 'specialist1@example.com'})
    self.assertRedirects(response, reverse('home_page'))

    profile = UserProfile.objects.get(user__email='john.doe4@example.com')
    pro = User.objects.get(email='specialist1@example.com')
    self.assertEquals(profile.current_pro, pro)

    # check that emails are sent to vinely + pro
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com', u'specialist1@example.com']", subject='A Vinely Taste Party is ready to be scheduled')
    self.assertTrue(vinely_recipients.exists())

    # check that emails are sent to recipient
    host_recipient = Email.objects.filter(recipients="[u'john.doe4@example.com']", subject='Get the party started with Vinely')
    self.assertTrue(host_recipient.exists())

    self.client.logout()

    # 6. Anonymous sign up as host - no pro specified
    response = self.client.post(reverse("make_host", args=['signup']), {'first_name': 'John',
                                                                        'last_name': 'Doe5',
                                                                        'email': 'john.doe5@example.com',
                                                                        'password1': 'Sign Up',
                                                                        'password2': 'Sign Up',
                                                                        'zipcode': '92612',
                                                                        'phone_number': '6172342524'})
    self.assertRedirects(response, reverse('home_page'))

    # check no pro assigned
    profile = UserProfile.objects.get(user__email='john.doe5@example.com')
    self.assertEquals(profile.current_pro, None)

    # check that emails are sent to vinely + pro
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com']", subject='A Vinely Taste Party is ready to be scheduled')
    self.assertTrue(vinely_recipients.exists())

    # check that emails are sent to recipient
    host_recipient = Email.objects.filter(recipients="[u'john.doe5@example.com']", subject='Get the party started with Vinely')
    self.assertTrue(host_recipient.exists())

    self.client.logout()

    # 7. Anonymous signs up with fake pro email
    response = self.client.post(reverse("make_host", args=['signup']), {'first_name': 'John',
                                                                        'last_name': 'Doe6',
                                                                        'email': 'john.doe6@example.com',
                                                                        'password1': 'Sign Up',
                                                                        'password2': 'Sign Up',
                                                                        'zipcode': '92612',
                                                                        'phone_number': '6172342524',
                                                                        'mentor': 'no.pro@example.com'})
    self.assertContains(response, "The Pro email you specified is not for a Vinley Pro")

    # logged in as taster, sign up to be host - with pro
    response = self.client.login(email="attendee2@example.com", password="hello")
    self.assertEquals(response, True)

    response = self.client.get(reverse("make_host", args=['signup']))
    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("make_host", args=['signup']), {'first_name': 'attendee',
                                                                        'last_name': 'two',
                                                                        'password1': 'Sign Up',
                                                                        'password2': 'Sign Up',
                                                                        'email': 'attendee2@example.com',
                                                                        'phone_number': '6172342524',
                                                                        'zipcode': '49546',
                                                                        'mentor': 'specialist1@example.com'})
    self.assertRedirects(response, reverse('home_page'))
    # self.assertContains(response, "To ensure that Vinely emails get to your inbox, please add info@vinely.com to your email Address Book or Safe List.")

    # check no pro assigned
    profile = UserProfile.objects.get(user__email='attendee2@example.com')
    pro = User.objects.get(email='specialist1@example.com')
    self.assertEquals(profile.current_pro, pro)

    # check that emails are sent to vinely
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com']", subject='A Vinely Taste Party is ready to be scheduled')
    self.assertTrue(vinely_recipients.exists())

    # check that emails are sent to taster
    host_recipient = Email.objects.filter(recipients="[u'attendee2@example.com']", subject='Get the party started with Vinely')
    self.assertTrue(host_recipient.exists())

    self.client.logout()

    # logged in as taster, sign up to be host - no pro
    response = self.client.login(email="attendee3@example.com", password="hello")
    self.assertEquals(response, True)

    response = self.client.get(reverse("make_host", args=['signup']))
    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("make_host", args=['signup']), {'first_name': 'attendee',
                                                                        'last_name': 'three',
                                                                        'password1': 'Sign Up',
                                                                        'password2': 'Sign Up',
                                                                        'email': 'attendee3@example.com',
                                                                        'phone_number': '6172342524',
                                                                        'zipcode': '49546'})
    self.assertRedirects(response, reverse('home_page'))
    # self.assertContains(response, "To ensure that Vinely emails get to your inbox, please add info@vinely.com to your email Address Book or Safe List.")

    # check no pro assigned
    profile = UserProfile.objects.get(user__email='attendee3@example.com')
    self.assertEquals(profile.current_pro, None)

    # check that emails are sent to vinely
    vinely_recipients = Email.objects.filter(recipients="['sales@vinely.com']", subject='A Vinely Taste Party is ready to be scheduled')
    self.assertTrue(vinely_recipients.exists())

    # check that emails are sent to taster
    host_recipient = Email.objects.filter(recipients="[u'attendee3@example.com']", subject='Get the party started with Vinely')
    self.assertTrue(host_recipient.exists())

  def test_pro_approval(self):
    response = self.client.login(email="elizabeth@vinely.com", password="egoede")
    self.assertEquals(response, True)

    pro = User.objects.get(email='attendee1@example.com')
    pro.userprofile.role = UserProfile.ROLE_CHOICES[5][0]
    pro.userprofile.save()
    self.assertTrue(pro.userprofile.is_pending_pro())

    post_data = {
        'index': 0,
        'action': 'approve_pro',
        '_selected_action': pro.userprofile.id
    }

    response = self.client.post('/admin/accounts/userprofile/', post_data)
    self.assertEqual(response.status_code, 302)
    self.assertTrue(pro.get_profile().is_pro())

    # emails sent
    pro_approved_emails = Email.objects.filter(recipients="[u'attendee1@example.com']", subject='Vinely Pro Approved!')
    self.assertTrue(pro_approved_emails.exists())

  def test_mentor_assignment(self):
    response = self.client.login(email="elizabeth@vinely.com", password="egoede")
    self.assertEquals(response, True)

    pro = User.objects.get(email='attendee1@example.com')
    pro.userprofile.role = UserProfile.ROLE_CHOICES[1][0]
    pro.userprofile.save()
    self.assertTrue(pro.userprofile.is_pro())

    mentor = User.objects.get(email='specialist1@example.com')

    post_data = {
        '_save': 'Save',
        'user': pro.id,
        'mentor': mentor.id,
        'gender': pro.userprofile.gender,
        'role': UserProfile.ROLE_CHOICES[1][0],
        'wine_personality': pro.userprofile.wine_personality.id,
        '_selected_action': pro.userprofile.id
    }

    response = self.client.post('/admin/accounts/userprofile/%d/' % pro.userprofile.id, post_data)
    self.assertRedirects(response, '/admin/accounts/userprofile/')
    self.assertEquals(pro.get_profile().mentor, mentor)

    # emails sent
    mentor_assigned_emails = Email.objects.filter(recipients="[u'attendee1@example.com']", subject='Congratulations! Vinely Mentor has been assigned to you.')
    self.assertTrue(mentor_assigned_emails.exists())

    mentee_assigned_emails = Email.objects.filter(recipients="[u'specialist1@example.com']", subject='Congratulations! Vinely Mentee has been assigned to you.')
    self.assertTrue(mentee_assigned_emails.exists())

  def test_my_information_update(self):
    response = self.client.login(email="attendee2@example.com", password="hello")
    self.assertEquals(response, True)

    # modify only basic info
    response = self.client.get(reverse("my_information"))
    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("my_information"), {'user_form': 'user_form',
                                                            'user-first_name': 'Jane',
                                                            'user-last_name': 'Doe',
                                                            'user-email': 'attendee2@example.com'})

    self.assertContains(response, "Errors were encountered when trying to update your information. Please correct them and retry the update.")

    # change e-mail address
    response = self.client.post(reverse("my_information"), {'user_form': 'user_form',
                                                            'user-first_name': 'Jane',
                                                            'user-last_name': 'Doe',
                                                            'user-email': 'john.doe@example.com',
                                                            'profile-phone': '617-345-2342'})

    self.assertContains(response, "Your information has been updated")

    response = self.client.post(reverse("my_information"), {'user_form': 'user_form',
                                                            'profile-phone': '617-234-2524',
                                                            'user-last_name': 'Doe',
                                                            'user-email': 'john.doe@example.com'})

    self.assertContains(response, "Errors were encountered when trying to update your information. Please correct them and retry the update.")

    # modify only shipping
    response = self.client.post(reverse("my_information"), {'shipping-street1': '55 Memorial Dr.',
                                                            'shipping-street2': '#14',
                                                            'shipping-city': 'North Haven',
                                                            'shipping-state': 'CT',
                                                            'shipping-zipcode': '48105',
                                                            'shipping_form': 'shipping_form'})

    self.assertContains(response, "Your information has been updated")

    response = self.client.post(reverse("my_information"), {'shipping-street1': '55 Memorial Dr.',
                                                            'shipping-city': 'North Haven',
                                                            'shipping-state': 'CT',
                                                            'shipping-zipcode': '48105',
                                                            'shipping_form': 'shipping_form'})

    self.assertContains(response, "Your information has been updated")

    response = self.client.post(reverse("my_information"), {'shipping-street1': '140 Columbia St.',
                                                            'shipping-city': 'Detroit',
                                                            'shipping-zipcode': '48115',
                                                            'shipping_form': 'shipping_form'})

    self.assertContains(response, "Errors were encountered when trying to update your information. Please correct them and retry the update.")

    """ Billing form no longer exists
    # modify only billing
    response = self.client.post(reverse("my_information"), {'billing-street1': '140 Columbia St.',
                                                            'billing-street2': '#2',
                                                            'billing-city': 'Cambridge',
                                                            'billing-state': 'MA',
                                                            'billing-zipcode': '02139',
                                                            'billing_form': 'billing_form'})

    self.assertContains(response, "Your information has been updated")

    response = self.client.post(reverse("my_information"), {'billing-street1': '140 Columbia St.',
                                                            'billing-city': 'Detroit',
                                                            'billing-zipcode': '48115',
                                                            'billing_form': 'billing_form'})

    self.assertContains(response, "Errors were encountered when trying to update your information. Please correct them and retry the update.")

    response = self.client.post(reverse("my_information"), {'billing-city': 'Detroit',
                                                            'billing-state': 'MI',
                                                            'billing-zipcode': '48115',
                                                            'billing_form': 'billing_form'})

    self.assertContains(response, "This field is required")
    """

    # modify only payment
    response = self.client.post(reverse("my_information"), {'payment-card_type': 'Unknown',
                                                            'payment-card_number': '4111111111111111',
                                                            'payment-exp_month': '7',
                                                            'payment-exp_year': '2013',
                                                            'payment-verification_code': '555',
                                                            'payment-billing_zipcode': '48105',
                                                            'payment_form': 'payment_form'})

    self.assertContains(response, "Your information has been updated")

    response = self.client.post(reverse("my_information"), {'payment-card_number': '4111111111111111111',
                                                            'payment-exp_month': '8',
                                                            'payment-exp_year': '2015',
                                                            'payment-billing_zipcode': '48105',
                                                            'payment_form': 'payment_form'})

    self.assertContains(response, "This field is required")

    response = self.client.post(reverse("my_information"), {'payment-card_type': 'Visa',
                                                            'payment-card_number': '4111111111111111',
                                                            'payment-exp_month': '8',
                                                            'payment-exp_year': '2015',
                                                            'payment-verification_code': '342',
                                                            'payment-billing_zipcode': '48105',
                                                            'payment_form': 'payment_form'})

    self.assertContains(response, "Your information has been updated")

    print "Information update test all work"

  def test_user_rsvp_without_signup(self):
    pass

  def test_make_host(self):
    pass

  def test_make_pro(self):
    pass

  def test_basic_addition(self):
    """
    Tests that 1 + 1 always equals 2.
    """
    self.assertEqual(1 + 1, 2)
