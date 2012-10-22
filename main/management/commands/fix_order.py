from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from main.models import Product, Order, LineItem
from main.tests import SimpleTest

class Command(BaseCommand):
  args = ""
  help = "Script used to fix previous order that referred to old product ID"

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
    # TODO: need to specify order_id, product_id, price_category, quantity, frequency

    o = Order.objects.get(id=1)
    cart = o.cart

    # superior collection
    p = Product.objects.get(id=5)
    # full case
    item = LineItem(product=p, price_category=7, quantity=1, frequency=2)
    item.total_price = item.subtotal()
    item.save()
    cart.items.add(item)
    cart.save()