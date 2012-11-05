from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

from optparse import make_option
from datetime import datetime

from accounts.models import CreditCard
from main.models import SubscriptionInfo, CustomizeOrder, Party, PartyInvite
from personality.models import WinePersonality, Wine, WineRatingData

import xlrd

class Command(BaseCommand):

  args = ''
  help = 'Read orders that have not been recorded'

  option_list = BaseCommand.option_list + (
    make_option('-f', '--file',
            type='string',
            dest='filename',
            default=None,
            help='The excel file name of master database.'),
    )

  def handle(self, *args, **options):
    # Read excel file, go through each column

    wb = xlrd.open_workbook("docs/new_orders_10292012.xlsx")
    sheet = wb.sheet_by_name("Orders")

    print sheet.nrows
    for rownum in range(1, 6):
      row = sheet.row_values(rownum)
      # find user first

      customer_email = row[20].strip().lower()
      try:
        u = User.objects.get(email=customer_email)
      except User.DoesNotExist:
        


      # cart, item

      #Cart.objects.get_or_create()

      #CustomizeOrder.objects.get_or_create(user=u)
      # create shipping address

      # create credit CreditCard

      # create order

      # save everything