"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse


class SimpleTest(TestCase):

    def setUp(self):
      pass

    def test_xoauth(self):
      response = self.client.post(reverse('get_xoauth_gmail'), {
            "user": "kbaranowski@redstar.com",
            "token": "1/yypfkV2FmS_2BHEomTHYiYPFWr9Mv7SP7_Iip95Nph8",
            "secret": "UOhGFM77U1PJOkwKIy-cF4EO",
        })

      print response.content 
      print response.status_code
