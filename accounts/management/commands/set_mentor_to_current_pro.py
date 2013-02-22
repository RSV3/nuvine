from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounts.models import UserProfile
from main.models import PartyInvite, MyHost, Order


class Command(BaseCommand):
  args = ''
  help = 'Set mentor field to the current pro'

  def handle(self, *args, **options):
    profiles = UserProfile.objects.all()
    user_count = 0
    for profile in profiles:
      user = profile.user
      if profile.is_pro():
        pass
      elif profile.is_host():
        mypros = MyHost.objects.filter(host=user, pro__isnull=False).order_by('-timestamp')
        if mypros.exists():
          pro = mypros[0].pro
          profile.mentor = pro
          profile.save()
          user_count += 1
          # print "update %s" % profile.user
      elif profile.is_taster():
        # find most recent subscription purchase made by user
        orders = Order.objects.filter(cart__receiver=profile.user, cart__party__isnull=False, cart__items__frequency__in=[1, 2, 3]).order_by('-order_date')
        if orders.exists():
          pro = orders[0].cart.party.pro
          profile.mentor = pro
          profile.save()
          user_count += 1
          # print "update %s" % profile.user
        else:
          # find pro and host who invited first
          invitation = PartyInvite.objects.filter(invitee=user).order_by('invited_timestamp')
          if invitation.exists():
            # find pro that arranged party for my host
            pro = invitation[0].party.pro
            profile.mentor = pro
            profile.save()
            user_count += 1
            # print "update %s" % profile.user

    print "Updated the mentor entry for %s profiles" % user_count
