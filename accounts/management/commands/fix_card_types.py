from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounts.models import CreditCard
from creditcard.fields import *

class Command(BaseCommand):
  args = ''
  help = 'Fix credit card type'

  def handle(self, *args, **options):

    card_field = CreditCardField()
    for card in CreditCard.objects.all():
      card.card_type = card_field.get_cc_type(card.decrypt_card_num())
      card.save()
