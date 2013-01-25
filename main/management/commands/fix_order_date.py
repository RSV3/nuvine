from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from main.models import Order, PartyInvite
from accounts.models import SubscriptionInfo

class Command(BaseCommand):
  args = ""
  help = "Go through the orders and set them to the initial party date if they were added on Nov 28"

  option_list = BaseCommand.option_list + (
    make_option('-m', '--mutual',
            action='store_true',
            dest='mutual',
            default=False,
            help='Find the number of mutual friends and sort by them'),
    make_option('-p', '--posts',
            action='store_true',
            dest='posts',
            default=False,
            help="Prioritize those that have posted on the user's wall and then those users where user has posted")
    )

  def handle(self, *args, **options):
    for receiver_email in Order.objects.values_list('receiver__email', flat=True).distinct():
      subscription = SubscriptionInfo.objects.filter(user__email=receiver_email).order_by('-updated_datetime')
      if subscription.exists():
        subscription = subscription[0]
        print subscription.get_frequency_display()
      else:
        print "No subscription"

      # item.price_category == 11 then it's host tasting kit (date should be 5 days before party)
      # item.frequency == [0, 9] no subscription
      # item.frequency == 1  monthly
      # item.frequency == 2  bi-monthly
      # item.frequency == 3  quarterly

      # for each user that has ordered
      last_order_date = None
      for o in Order.objects.filter(receiver__email=receiver_email).order_by('id'):
        tasting_kit = False
        frequency = 0

        for item in o.cart.items.all():
          if item.price_category == 11:
            tasting_kit = True
            break
          frequency = item.frequency

        print o.receiver.email, 
        print o.get_fulfill_status_display(), [item for item in o.cart.items.all()]

        invites = PartyInvite.objects.filter(invitee=o.receiver, party__event_date__lt=datetime.today()).order_by('party__event_date')
        if invites.exists():
          # first party invite date
          inv = invites[0]
          diff_days = o.order_date - inv.party.event_date
          if diff_days.days > 7:
            if tasting_kit:
              o.order_date = inv.party.event_date - timedelta(days=5)
            elif frequency == [0, 9]:
              # it's wine subscription use frequency
              o.order_date = inv.party.event_date + timedelta(days=1)
              last_order_date = o.order_date
            else:
              if not last_order_date:
                o.order_date = inv.party.event_date + timedelta(days=1)
              else:
                o.order_date = last_order_date + relativedelta(months=+frequency)
              last_order_date = o.order_date
            o.save()
          else:
            print "%s - %s - Order data did not change" % (o.vinely_order_id, o.receiver.email)

          diff_days = o.order_date - inv.party.event_date
          print "\tNew Order date: %s - Party date: %s - Days diff: %s" % (o.order_date, inv.party.event_date, diff_days.days)
        else:
          print "\tOrder date: %s - No parties" % o.order_date
