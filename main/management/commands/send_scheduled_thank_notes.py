from django.core.management.base import BaseCommand
from main.models import Party, Order, PartyInvite, ThankYouNote
from django.utils import timezone
from datetime import timedelta
from django.http import HttpRequest

from main.utils import distribute_party_thanks_note_email


class Command(BaseCommand):
  args = ""
  help = "Send party thank you notes after a party"

  def handle(self, *args, **options):
    request = HttpRequest()
    request.META['SERVER_NAME'] = "www.vinely.com"
    request.META['SERVER_PORT'] = 80
    request.session = {}

    today = timezone.now()
    yester = today - timedelta(hours=24)
    limit = today - timedelta(hours=48)
    for party in Party.objects.filter(event_date__lte=yester, event_date__gt=limit, auto_thank_you=True):
      # party = Party.objects.get(pk=party_id)
      note_sent = ThankYouNote.objects.create(party=party)
      invitees = PartyInvite.objects.filter(party=party).exclude(invitee=party.host)
      orders = Order.objects.filter(cart__party=party)
      buyers = invitees.filter(invitee__in=[x.receiver for x in orders])
      non_buyers = invitees.exclude(invitee__in=[x.receiver for x in orders])

      request.user = party.host

      if non_buyers:
        distribute_party_thanks_note_email(request, note_sent, non_buyers, placed_order=False)
      if buyers:
        distribute_party_thanks_note_email(request, note_sent, buyers, placed_order=True)
