from django.core.management.base import BaseCommand, CommandError

from personality.models import WineRatingData

import csv

class Command(BaseCommand):
  args = ''
  help = 'Exports wine rating data of a user to a csv file for future import'

  def handle(self, *args, **options):
    
    # TODO: need to load from csv 

    # TODO: need to see if there's a user with a particular e-mail, if not exist create user
    #       need to see if there's a wine with a particular id and if different search for the name of wine if no wine, create the wine 

    #       save wine rating data

