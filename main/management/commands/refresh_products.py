from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from main.models import Product
from main.tests import SimpleTest

class Command(BaseCommand):
  args = ""
  help = "Manually initialize products"

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
    for p in Product.objects.all():
      p.delete()

    s = SimpleTest()
    s.create_products()
