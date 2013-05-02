from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from accounts.models import UserProfile

class Command(BaseCommand):
  args = ''
  help = 'Migrate roles from groups to new roles field in UserProfile'

  def handle(self, *args, **options):
    for prof in UserProfile.objects.all():

      user = prof.user

      pro_group = Group.objects.get(name='Vinely Pro')
      hos_group = Group.objects.get(name='Vinely Host')
      tas_group = Group.objects.get(name='Vinely Taster')
      sup_group = Group.objects.get(name='Supplier')     
      pen_group = Group.objects.get(name='Pending Vinely Pro')

      groups = user.groups.all()
      if pro_group in groups:
        prof.role = UserProfile.ROLE_CHOICES[1][0]
      elif hos_group in groups:
        prof.role = UserProfile.ROLE_CHOICES[2][0]
      elif tas_group in groups:
        prof.role = UserProfile.ROLE_CHOICES[3][0]
      elif sup_group in groups:
        prof.role = UserProfile.ROLE_CHOICES[4][0]
      elif pen_group in groups:
        prof.role = UserProfile.ROLE_CHOICES[5][0]

      prof.save()
