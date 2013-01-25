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
from django.db.models import Q
from main.utils import send_order_confirmation_email

import stripe


class Command(BaseCommand):

  args = ''
  help = 'Daily process to check the subscription information, create new order and add next order if they are due today'

  def handle(self, *args, **options):
    # Get all users whose subscriptions are not already being handled by stripe
    for user_id in SubscriptionInfo.objects.exclude(Q(frequency__in=[0, 9]) | Q(quantity=0) | Q(user__userprofile__stripe_card__isnull=False)).values_list('user', flat=True).distinct():
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
            # product = Product.objects.get(id=4)
            product = Product.objects.get(cart_tag='basic')
          elif subscription.quantity == 7:
            # product = Product.objects.get(id=5)
            product = Product.objects.get(cart_tag='divine')
          elif subscription.quantity == 9:
            # product = Product.objects.get(id=6)
            product = Product.objects.get(cart_tag='superior')
        elif subscription.quantity in [6, 8, 10]:
          # half case
          quantity_code = 2
          if subscription.quantity == 6:
            # product = Product.objects.get(id=4)
            product = Product.objects.get(cart_tag='basic')
          elif subscription.quantity == 8:
            # product = Product.objects.get(id=5)
            product = Product.objects.get(cart_tag='divine')
          elif subscription.quantity == 10:
            # product = Product.objects.get(id=6)
            product = Product.objects.get(cart_tag='superior')
        elif subscription.quantity in [12, 13, 14]:
          quantity_code = 3
          if subscription.quantity == 12:
            product = Product.objects.get(cart_tag='3')
          elif subscription.quantity == 13:
            product = Product.objects.get(cart_tag='6')
          elif subscription.quantity == 14:
            product = Product.objects.get(cart_tag='12')

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

        # determine if need to use stripe or native processing
        receiver_state = shipping_address.state

        if receiver_state in Cart.STRIPE_STATES:
          if receiver_state == 'MI':
            stripe.api_key = settings.STRIPE_SECRET
          elif receiver_state == 'CA':
            stripe.api_key = settings.STRIPE_SECRET_CA
          credit_card = prof.credit_card

          if settings.DEPLOY:
            card_number = credit_card.decrypt_card_num()
            cvc = credit_card.decrypt_cvv()
          else:
            cvc = '111'
            if credit_card.card_type == 'American Express':
              card_number = '378282246310005'
            elif credit_card.card_type == 'Master Card':
              card_number = '5105105105105100'
            else:
              card_number = '4242424242424242'

          card = {'number': card_number, 'exp_month': credit_card.exp_month, 'exp_year': credit_card.exp_year,
                  'name': '%s %s' % (user.first_name, user.last_name), 'address_zip': credit_card.billing_zipcode,
                  }

          # some cards dont have a verification code so only include cvc for those that have
          if cvc:
            card['cvc'] = cvc

          # no record of this customer-card mapping so create
          try:
            customer = stripe.Customer.create(card=card, email=user.email)
            # up profile
            stripe_card = StripeCard.objects.create(stripe_user=customer.id, exp_month=customer.active_card.exp_month,
                                exp_year=customer.active_card.exp_year, last_four=customer.active_card.last4,
                                card_type=customer.active_card.type, billing_zipcode=credit_card.billing_zipcode)

            prof.stripe_card = stripe_card
            prof.save()
            prof.stripe_cards.add(stripe_card)

            stripe.InvoiceItem.create(customer=customer.id, amount=int(order.cart.tax() * 100), currency='usd', description='Tax')
            stripe_plan = SubscriptionInfo.STRIPE_PLAN[item.frequency][item.price_category - 5]
            customer.update_subscription(plan=stripe_plan)
          except Exception, e:
            print "Error processing card with stripe", e
            print 'Card was declined by stripe for %s %s <%s>' % (user.first_name, user.last_name, user.email)

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
