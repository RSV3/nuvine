from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from datetime import datetime, timedelta
from main.models import Order, PartyInvite

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
      for o in Order.objects.filter(receiver__email=receiver_email):
        print o.receiver.email, 
        print o.get_fulfill_status_display(), [item for item in o.cart.items.all()]

        invites = PartyInvite.objects.filter(invitee=o.receiver, party__event_date__lt=datetime.today()).order_by('party__event_date')
        if invites.exists():
          # first party invite date
          inv = invites[0]
          diff_days = o.order_date - inv.party.event_date
          if diff_days.days > 5:
            o.order_date = inv.party.event_date + timedelta(days=1)
            o.save()
          print "\tOrder date: %s - Party date: %s - Days diff: %s" % (o.order_date, inv.party.event_date, diff_days.days)
        else:
          print "\tOrder date: %s - No parties" % o.order_date
