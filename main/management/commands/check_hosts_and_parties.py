from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from accounts.models import User
from main.models import NewHostNoParty, UnconfirmedParty, Party
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
  args = ""
  help = "Checks for hosts that havent created a party 7 days after signing up and parties that havent been confirmed 48 hrs after being created"

  def handle(self, *args, **options):
    # 1. hosts with no parties
    hosts_with_parties = Party.objects.values_list('host', flat=True).distinct()

    # if host created a party after being in the list, remove them
    NewHostNoParty.objects.filter(host__id__in=hosts_with_parties).delete()
    already_listed = NewHostNoParty.objects.values_list('host', flat=True)

    seven_ago = timezone.now() - timedelta(days=7)
    # hosts with no parties
    hosts_no_party = User.objects.filter(groups__name='Vinely Host', date_joined__lt=seven_ago).exclude(Q(id__in=hosts_with_parties) | Q(id__in=already_listed)).values_list('id', flat=True)
    # print 'no party', hosts_no_party
    hosts = User.objects.filter(id__in=hosts_no_party)
    for host in hosts:
      NewHostNoParty.objects.create(host=host)

    # 2. Unconfirmed parties
    two_ago = timezone.now() - timedelta(days=2)
    confirmed_parties = Party.objects.filter(confirmed=True)
    UnconfirmedParty.objects.filter(party__in=confirmed_parties).delete()
    already_listed = UnconfirmedParty.objects.values_list('party', flat=True)
    unconfirmed_parties = Party.objects.filter(confirmed=False, requested=True, created__lt=two_ago).exclude(id__in=already_listed)

    for party in unconfirmed_parties:
      UnconfirmedParty.objects.create(party=party)

