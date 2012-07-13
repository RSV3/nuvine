from django.core.management.base import BaseCommand, CommandError

from personality.models import WineRatingData

import csv

class Command(BaseCommand):
  args = ''
  help = 'Exports wine rating data of a user to a csv file for future import'

  def handle(self, *args, **options):
    
    # TODO: need to save email, first_name, last_name

    # TODO: need to save wine id, and all wine information (name, description etc) just in case id is different


