from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.contrib.auth.models import User
from main.models import LineItem, Cart, Order, Product
from accounts.models import SubscriptionInfo
from main.utils import UTC

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.http import HttpRequest


class Command(BaseCommand):

  args = ''
  help = 'Daily process to check the subscription information and add new orders'

  def handle(self, *args, **options):

    for user_id in SubscriptionInfo.objects.exclude(frequency__in=[0,9]).filter(quantity__gt=0).values_list('user', flat=True).distinct():
      user = User.objects.get(id=user_id)

      # need to add new orders
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

        cart = Cart(user=user, adds=1)
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

        # TODO: need to charge credit card if necessary

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
        request.META['SERVER_PORT'] = 443
        request.user = user
        request.session = {}

        send_order_confirmation_email(request, order.order_id)
        send_to_supplier_order_added_email(request, order.order_id)
      else:
        days_left = subscription.next_invoice_date - date.today()
        print "%d days left for %s %s <%s> new order" % (days_left.days, user.first_name, user.last_name, user.email)
