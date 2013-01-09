from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.contrib.auth.models import User
from main.models import LineItem, Cart, Order, Product, PartyInvite
from accounts.models import SubscriptionInfo, Zipcode
from stripecard.models import StripeCard
from main.utils import UTC

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.http import HttpRequest
from django.conf import settings

from main.utils import send_order_confirmation_email

import stripe

class Command(BaseCommand):

  args = ''
  help = 'Daily process to check the subscription information, create new order and add next order if they are due today'

  def handle(self, *args, **options):

    for user_id in SubscriptionInfo.objects.exclude(frequency__in=[0, 9]).filter(quantity__gt=0).values_list('user', flat=True).distinct():
      user = User.objects.get(id=user_id)

      # need to work with only the latest subscription info per user
      subscription = SubscriptionInfo.objects.filter(user=user).order_by('-updated_datetime')[0]

      if subscription.quantity == 0 or subscription.frequency in [0, 9]:
        print "%s %s <%s> has no subscription" % (user.first_name, user.last_name, user.email)
        continue

      if subscription.next_invoice_date == date.today():
        product = None
        if subscription.quantity in [5, 7, 9]:
          # full case
          quantity_code = 1
          if subscription.quantity == 5:
            product = Product.objects.get(id=4)
          elif subscription.quantity == 7:
            product = Product.objects.get(id=5)
          elif subscription.quantity == 9:
            product = Product.objects.get(id=6)
        elif subscription.quantity in [6, 8, 10]:
          # half case
          quantity_code = 2
          if subscription.quantity == 6:
            product = Product.objects.get(id=4)
          elif subscription.quantity == 8:
            product = Product.objects.get(id=5)
          elif subscription.quantity == 10:
            product = Product.objects.get(id=6)

        if product is None:
          print "%s %s <%s> does not have a subscription product" % (user.first_name, user.last_name, user.email)

        item = LineItem(product=product, price_category=subscription.quantity, quantity=quantity_code, frequency=subscription.frequency)
        item.save()

        # party should be same as from last order or first party they participated in
        first_invite = None
        invites = PartyInvite.objects.filter(invitee=user).order_by('party__event_date')
        if invites.exists():
          first_invite = invites[0]
          print "First party date:", first_invite.party.event_date
        else:
          print "No first party for:", user.email

        # find party from last order
        last_order = None
        all_orders = Order.objects.filter(receiver=user).order_by('-order_date')
        if all_orders.exists():
          last_order = all_orders[0]

        cart = Cart(user=user, receiver=user, adds=1)
        if last_order and last_order.cart.party:
          cart.party = last_order.cart.party
        elif first_invite:
          cart.party = first_invite.party
        else:
          # there's no party to associate to
          print "There's no party for:", user.email
        cart.save()
        cart.items.add(item)
        cart.save()

        prof = user.get_profile()
        shipping_address = prof.shipping_address
        card = prof.credit_card
        today = datetime.now(tz=UTC())
        order = Order(ordered_by=user, receiver=user, cart=cart,
              shipping_address=shipping_address, credit_card=card, order_date=today)
        order.assign_new_order_id()
        order.save()
        print "Created a new order for %s %s <%s>" % (user.first_name, user.last_name, user.email)

        """
        # TODO: need to charge credit card if necessary
        receiver_state = Zipcode.objects.get(code=shipping_address.zipcode).state

        if receiver_state == "MI":
          stripe.api_key = settings.STRIPE_SECRET
          stripe_card = prof.stripe_card

          try:
            customer = stripe.Customer.retrieve(id=stripe_card.stripe_user)
            if customer.get('deleted'):
              raise Exception('Customer Deleted')
            stripe_user_id = customer.id

            # makes sure we have the exact same card
            stripe_card = StripeCard.objects.get(stripe_user=stripe_user_id, exp_month=request.POST.get('exp_month'),
                              exp_year=request.POST.get('exp_year'), last_four=request.POST.get('last4'),
                              card_type=request.POST.get('card_type'), billing_zipcode=request.POST.get('address_zip'))
          except:
            print "Stripe account does not work for:", user.email
            continue

          stripe.api_key = settings.STRIPE_SECRET
          # NOTE: Amount must be in cents
          # Having these first so that they come last in the stripe invoice.
          stripe.InvoiceItem.create(customer=prof.stripe_card.stripe_user, amount=int(order.cart.shipping() * 100), currency='usd', description='Shipping')
          stripe.InvoiceItem.create(customer=prof.stripe_card.stripe_user, amount=int(order.cart.tax() * 100), currency='usd', description='Tax')
          non_sub_orders = order.cart.items.filter(frequency=0)
          for item in non_sub_orders:
            # one-time only charged immediately at this point
            stripe.InvoiceItem.create(customer=prof.stripe_card.stripe_user, amount=int(item.subtotal() * 100), currency='usd', description=LineItem.PRICE_TYPE[item.price_category][1])

          # if subscription exists then create plan
          sub_orders = order.cart.items.filter(frequency__in=[1, 2, 3])
          if sub_orders.exists():
            item = sub_orders[0]
            customer = stripe.Customer.retrieve(id=prof.stripe_card.stripe_user)
            stripe_plan = SubscriptionInfo.STRIPE_PLAN[item.frequency][item.price_category - 5]
            customer.update_subscription(plan=stripe_plan)
        """

        # need to update next invoice date on subscription
        if subscription.frequency == 1:
          next_invoice = datetime.date(datetime.now(tz=UTC())) + relativedelta(months=+1)
        elif subscription.frequency == 2:
          next_invoice = datetime.date(datetime.now(tz=UTC())) + relativedelta(months=+2)
        elif subscription.frequency == 3:
          next_invoice = datetime.date(datetime.now(tz=UTC())) + relativedelta(months=+3)
        subscription.next_invoice_date = next_invoice
        subscription.save()

        # send out verification e-mail, create a verification code
        request = HttpRequest()
        request.META['SERVER_NAME'] = "www.vinely.com"
        request.META['SERVER_PORT'] = 80
        request.user = user
        request.session = {}

        send_order_confirmation_email(request, order.order_id)
      else:
        days_left = subscription.next_invoice_date - date.today()
        print "%d days left for %s %s <%s> new order" % (days_left.days, user.first_name, user.last_name, user.email)
