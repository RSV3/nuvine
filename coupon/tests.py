"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

from datetime import timedelta

from main.tests import SimpleTest as MainTest
from main.models import Product
from coupon.models import Coupon


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def setUp(self):
        """
        create usable accounts
        """
        # test = CMSTest()
        # test.create_all_templates()

        main_test = MainTest()
        main_test.create_usable_accounts()
        main_test.create_wine_personalities()
        main_test.create_wine_samplers()
        main_test.create_test_products()

    def test_create_coupon(self):
        response = self.client.login(email="elizabeth@vinely.com", password='egoede')
        self.assertTrue(response)

        response = self.client.get(reverse('coupon_list'))
        self.assertEquals(response.status_code, 200)

        # give both percent off and amount off
        # date must be in future
        # repeating coupon without duration
        # must have max redemptions
        redeem_date = timezone.now().strftime('%m/%d/%Y')
        response = self.client.post(reverse('coupon_create'), {
            'code': 'random_code',
            'name': 'Random Code',
            'percent_off': 0,
            'amount_off': 0,
            'redeem_by': redeem_date,
            'applies_to': [],
            'repeat_duration': 0,
            'duration': 2,
            'active': True,
            'max_redemptions': 0,
        })

        self.assertContains(response, 'Max redemptions must be 1 or more.')
        self.assertContains(response, 'Date must be in future')
        self.assertContains(response, 'You must set a value of 1 or more for either amount off or percent off.')
        self.assertContains(response, 'You must specify a repeat duration greater than 0 if it is repeating.')

        redeem_date = (timezone.now() + timedelta(days=20)).strftime('%m/%d/%Y')
        response = self.client.post(reverse('coupon_create'), {
            'code': 'random_code',
            'name': 'Random Code',
            'percent_off': 10,
            'amount_off': 0,
            'redeem_by': redeem_date,
            'applies_to': [x.id for x in Product.objects.all()],
            'repeat_duration': 0,
            'duration': 0,
            'active': True,
            'max_redemptions': 1,
        })

        self.assertRedirects(response, reverse('coupon_list'))
        self.assertTrue(Coupon.objects.filter(code='random_code').exists())

        # 1. try to create coupon with already existing code
        response = self.client.post(reverse('coupon_create'), {
            'code': 'random_code',
            'name': 'Random Code',
            'percent_off': 10,
            'amount_off': 10,
            'redeem_by': redeem_date,
            'applies_to': [x.id for x in Product.objects.all()],
            'repeat_duration': 0,
            'duration': 0,
            'active': True,
            'max_redemptions': 1,
        })
        self.assertContains(response, 'already exists')
        self.assertContains(response, 'You can only set either amount off or percent off but not both.')
