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
    make_option('-g', '--gender',
            action='store_true',
            dest='gender',
            default=False,
            help='Use gender and their facebook ID proximity to suggest'),
    make_option('-w', '--wall',
            action='store_true',
            dest='wall',
            default=False,
            help='Use the latest wall post date information to find people to suggest'),
    make_option('-s', '--semantic',
            action='store_true',
            dest='semantic',
            default=False,
            help='Use the wall semantic information to find out those users'),
    make_option('-a', '--apps',
            action='store_true',
            dest='apps',
            default=False,
            help="Find those who use apps and prioritize them first"), 
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

  
