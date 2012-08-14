"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from personality.models import SurveyWine

class SimpleTest(TestCase):

  def runTest(self):
    pass


  def setUp(self):
    pass

  def create_survey_wines(self):
    # red wines
    SurveyWine.objects.get_or_create(name='Cabernet Sauvignon', color=SurveyWine.COLOR_CHOICES[0][0])
    SurveyWine.objects.get_or_create(name='Malbec', color=SurveyWine.COLOR_CHOICES[0][0])   
    SurveyWine.objects.get_or_create(name='Merlot', color=SurveyWine.COLOR_CHOICES[0][0])   
    SurveyWine.objects.get_or_create(name='Syrah/Shiraz', color=SurveyWine.COLOR_CHOICES[0][0])   
    SurveyWine.objects.get_or_create(name='Pinot Noir', color=SurveyWine.COLOR_CHOICES[0][0])   
    SurveyWine.objects.get_or_create(name='Sweet Red', color=SurveyWine.COLOR_CHOICES[0][0])   

    # white wines
    SurveyWine.objects.get_or_create(name='Pinot Grigio', color=SurveyWine.COLOR_CHOICES[1][0])   
    SurveyWine.objects.get_or_create(name='Riesling', color=SurveyWine.COLOR_CHOICES[1][0])   
    SurveyWine.objects.get_or_create(name='Sauvignon Blanc', color=SurveyWine.COLOR_CHOICES[1][0])   
    SurveyWine.objects.get_or_create(name='Chardonnay', color=SurveyWine.COLOR_CHOICES[1][0])   
    SurveyWine.objects.get_or_create(name='Moscato', color=SurveyWine.COLOR_CHOICES[1][0])   

    # other wines
    SurveyWine.objects.get_or_create(name='Sparkling wines/champagnes', color=SurveyWine.COLOR_CHOICES[2][0])   
    SurveyWine.objects.get_or_create(name=u'Ros\xE9', color=SurveyWine.COLOR_CHOICES[2][0])   
    SurveyWine.objects.get_or_create(name='Dessert wines', color=SurveyWine.COLOR_CHOICES[2][0])   