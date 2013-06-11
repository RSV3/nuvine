from django.core.management.base import BaseCommand
from accounts.models import UserProfile
from django.db.models import Sum
from main.models import Party, Order
from django.utils import timezone


class Command(BaseCommand):
  args = ''
  help = 'Calculate account credits for those hosts that have earned them'

  def handle(self, *args, **options):

    hosts = UserProfile.objects.filter(role__in=[1, 2])
    print hosts.count()
    for host in hosts:
      if host.events_manager():
        continue
      # get all past parties hosted by host
      today = timezone.now()
      host_parties = Party.objects.filter(host=host, event_date__lt=today)

      # only calculate credit if they have hosted a party
      if not host_parties.exists():
        print '%s has no parties' % host.user
        continue

      available_credit = 0
      for party in host_parties:
        available_credit += party.credit()

      # deduct used credit
      orders = Order.objects.filter(cart__receiver=host, cart__discount__gt=0)
      credit_aggregate = orders.aggregate(total=Sum('cart__discount'))
      credit_used = credit_aggregate['total'] if credit_aggregate['total'] else 0
      applicable_credit = available_credit - credit_used
      host.account_credit = applicable_credit if applicable_credit > 0 else 0
      host.save()
      print 'Set %s credits for %s' % (host.account_credit, host.user)
