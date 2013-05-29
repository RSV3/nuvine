from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

from main.models import PartyInvite
from personality.models import GeneralTaste, WineTaste, WineRatingData

import csv

class Command(BaseCommand):

  args = ''
  help = 'Export survey data to Excel'

  def handle(self, *args, **options):
    """
      Export user id, zipcode, general taste, wine taste and rating data
    """

    fieldnames = [
      'ID', 'email', 'zipcode', 'drink_regularly', 'coffee_type', 'coffee_take', 'salty_food',
      'citrus', 'earthy', 'berries', 'artificial', 'new_flavors', 'typical_wine', 'red_body',
      'red_sweetness', 'red_acidity', 'red_color', 'red_wines_often_1', 'red_wines_often_2',
      'red_wines_other', 'red_wine_dislike', 'red_wine_dislike_other',
      'white_oak', 'white_sweetness', 'white_acidity', 'white_color', 'white_wines_often_1',
      'white_wines_often_2', 'white_wines_other', 'white_wine_dislike',
      'white_wine_dislike_other', 'other_wines_1', 'other_wines_2', 'other_wines_3',
      'wine_personality', 'wine1', 'wine2', 'wine3', 'wine4', 'wine5', 'wine6'
    ]

    f = open("vinely_survey_data.csv", "w")

    writer = csv.DictWriter(f, fieldnames)
    writer.writeheader()

    for general_survey in GeneralTaste.objects.all():
      data = {}

      user = general_survey.user
      data['ID'] = user.id
      data['email'] = user.email

      profile = user.get_profile()

      zipcode = None
      if profile.zipcode:
        zipcode = profile.zipcode
      else:
        # check billing address
        zipcode = profile.billing_address.zipcode if profile.billing_address else None
        if not zipcode:
          # check party
          for inv in PartyInvite.objects.filter(invitee=user):
            if inv.party.address:
              zipcode = inv.party.address.zipcode
              break

      data['zipcode'] = zipcode
      data['drink_regularly'] = general_survey.drink_regularly
      data['coffee_type'] = general_survey.coffee_type
      data['coffee_take'] = general_survey.coffee_take
      data['salty_food'] = general_survey.salty_food
      data['citrus'] = general_survey.citrus
      data['earthy'] = general_survey.earthy
      data['berries'] = general_survey.berries
      data['artificial'] = general_survey.artificial
      data['new_flavors'] = general_survey.new_flavors

      try:
        wine_survey = WineTaste.objects.get(user=user)
        data['typical_wine'] = wine_survey.typically_drink
        data['red_body'] = wine_survey.red_body
        data['red_sweetness'] = wine_survey.red_sweetness
        data['red_acidity'] = wine_survey.red_acidity
        data['red_color'] = wine_survey.red_color

        for i, red_wine in enumerate(wine_survey.red_wines_often.all()[:2]):
          data['red_wines_often_%d' % (i+1,)] = str(red_wine) 

        data['red_wines_other'] = wine_survey.red_wines_other

        data['red_wine_dislike'] = wine_survey.red_wine_dislike.name if wine_survey.red_wine_dislike else None

        data['red_wine_dislike_other'] = wine_survey.red_wine_dislike_other

        data['white_oak'] = wine_survey.white_oak
        data['white_sweetness'] = wine_survey.white_sweetness
        data['white_acidity'] = wine_survey.white_acidity
        data['white_color'] = wine_survey.white_color

        for i, white_wine in enumerate(wine_survey.white_wines_often.all()[:2]):
          data['white_wines_often_%d' % (i+1,)] = str(white_wine)

        data['white_wines_other'] = wine_survey.white_wines_other

        data['white_wine_dislike'] = wine_survey.white_wine_dislike.name if wine_survey.white_wine_dislike else None

        data['white_wine_dislike_other'] = wine_survey.white_wine_dislike_other

        for i, other_wine in enumerate(wine_survey.other_wines.all()[:3]):
          data['other_wines_%d' % (i+1,)] = str(other_wine)

      except WineTaste.DoesNotExist:
        pass

      data['wine_personality'] = unicode(profile.wine_personality)

      for rating in WineRatingData.objects.filter(user=user):
        data['wine%d' % (rating.wine.number,)] = rating.overall
      #print data
      writer.writerow(data)
    f.close()
