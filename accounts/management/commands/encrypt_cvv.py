from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounts.models import CreditCard

class Command(BaseCommand):
  args = ''
  help = 'Encrypt credit card cvv numbers'

  def handle(self, *args, **options):

    for card in CreditCard.objects.all():
      card.encrypt_cvv(card.verification_code) 
      card.save()
