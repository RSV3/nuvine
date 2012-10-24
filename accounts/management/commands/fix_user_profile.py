from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
  args = ''
  help = 'Add user profiles to users that lost user profile'

  def handle(self, *args, **options):

    for u in User.objects.all():
      try:
        u.get_profile()
      except UserProfile.DoesNotExist:
        print "Creating user profile for {email}".format(email=u.email)
        UserProfile.objects.create(user=u)
