from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounts.models import UserProfile
from main.models import PartyInvite, MyHost, Order


class Command(BaseCommand):
  args = ''
  help = 'Set mentor field and current_pro to the current pro for the user'

  def handle(self, *args, **options):
    profiles = UserProfile.objects.all()
    user_count = 0
    for profile in profiles:
      user = profile.user
      if profile.is_pro():
        print "%s has mentor pro: %s" % (user.email, profile.mentor.email if profile.mentor else None)
      elif profile.is_host():
        profile.mentor = None
        profile.save()
        orders = Order.objects.filter(cart__receiver=profile.user, cart__party__isnull=False, cart__items__frequency__in=[1, 2, 3]).order_by('-order_date')
        # TODO: Could have made a VIP purchase with another host after being linked to MyHost.
        # Check VIP first or MyHost?
        mypros = MyHost.objects.filter(host=user, pro__isnull=False).order_by('-timestamp')
        if mypros.exists():
          pro = mypros[0].pro
          profile.current_pro = pro
          profile.save()
          user_count += 1
        elif orders.exists():
          pro = orders[0].cart.party.pro
          profile.current_pro = pro
          profile.save()
          user_count += 1

          # print "update %s" % profile.user
      elif profile.is_taster():
        profile.mentor = None
        profile.save()
        # find most recent subscription purchase made by user
        orders = Order.objects.filter(cart__receiver=profile.user, cart__party__isnull=False, cart__items__frequency__in=[1, 2, 3]).order_by('-order_date')
        if orders.exists():
          pro = orders[0].cart.party.pro
          profile.current_pro = pro
          profile.save()
          user_count += 1
          # print "update %s" % profile.user
        else:
          # find pro and host who invited first
          invitation = PartyInvite.objects.filter(invitee=user).order_by('invited_timestamp')
          if invitation.exists():
            # find pro that arranged party for my host
            pro = invitation[0].party.pro
            profile.current_pro = pro
            profile.save()
            user_count += 1
            # print "update %s" % profile.user
      else:
        print "[%s] %s does not have a pro" % (user.groups.all()[0] if user.groups.count() > 0 else None, user.email)

    print "Updated the pro and mentor entries for %s profiles" % user_count
