from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from emailusernames.utils import _email_to_username

class Command(BaseCommand):
  args = ''
  help = 'Converts usernames to email hashes to fix loaddata, dumpdata problem'

  def handle(self, *args, **options):

    for u in User.objects.all():
      u.username = _email_to_username(u.email)
      u.save()
