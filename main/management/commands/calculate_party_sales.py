from django.core.management.base import BaseCommand
from main.models import Party, Order, PartyInvite, Product
from django.db.models import Sum
from decimal import Decimal


class Command(BaseCommand):
  args = ""
  help = "Calculate the party sales per party and per invitee"

  def handle(self, *args, **options):
    invites = PartyInvite.objects.all()
    for invite in invites:
      orders = Order.objects.filter(receiver=invite.invitee, cart__party=invite.party)
      orders = orders.exclude(cart__items__product__category=Product.PRODUCT_TYPE[0][0])
      # aggregate = orders.aggregate(total=Sum('cart__items__total_price'))
      invite.sales = 0
      for order in orders:
        invite.sales += Decimal(order.cart.subtotal())
      invite.save()

    parties = Party.objects.all()
    for party in parties:
      aggregate = party.partyinvite_set.aggregate(total=Sum('sales'))
      party.sales = aggregate['total'] if aggregate['total'] else 0
      party.save()
