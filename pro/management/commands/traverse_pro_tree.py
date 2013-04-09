from django.core.management.base import BaseCommand
from optparse import make_option

from datetime import date, datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from pro.models import ProLevel

def find_root(pro_comp, start_pro):
  pro_comp[start_pro.id]['traversed'] = True
  upline_pro = pro_comp[start_pro.id]['upline']
  if upline_pro:
    # if there's upline, recurse
    root_pro = find_root(pro_comp, upline_pro)
  else:
    # it's the root pro
    return start_pro
  return root_pro


def qualify_tree(pro_comp, root_pro):
  num_active_pros = 0
  num_advanced_pros = 0
  num_elite_pros = 0
  downline_total_sales = 0

  # do a breadth first traverse through the tree
  for downline_pro in pro_comp[root_pro.id]['downline']:
    if pro_comp[downline_pro.id]['downline']:
      # if there are down line pro's then recurse
      qualify_tree(pro_comp, downline_pro)

    # add up downlines
    downline_total_sales += pro_comp[downline_pro.id]['total_sales']
    if pro_comp[downline_pro.id]['level'] == ProLevel.PRO_LEVEL_CHOICES[1][0]:
      num_active_pro += 1
    elif pro_comp[downline_pro.id]['level'] == ProLevel.PRO_LEVEL_CHOICES[2][0]:
      num_advanced_pro += 1
    elif pro_comp[downline_pro.id]['level'] == ProLevel.PRO_LEVEL_CHOICES[3][0]:
      num_elite_pro += 1

  # sum up all the downline and then qualify root_pro
  root_total_sales = pro_comp[root_pro.id]['total_sales']
  if (root_total_sales >= 10000
              and num_active_pros >= 10
              and num_advanced_pros >= 5
              and num_elite_pros >= 1):
    pro_comp[root_pro.id]['level'] = ProLevel.PRO_LEVEL_CHOICES[4][0]
  elif (root_total_sales >= 7800
              and num_active_pros >= 6
              and num_advanced_pros >= 2):
    pro_comp[root_pro.id]['level'] = ProLevel.PRO_LEVEL_CHOICES[3][0]
  elif (root_total_sales >= 5000
              and num_active_pros >= 3):
    pro_comp[root_pro.id]['level'] = ProLevel.PRO_LEVEL_CHOICES[2][0]
  elif (root_total_sales >= 1500
              and downline_total_sales >= 1200):
    pro_comp[root_pro.id]['level'] = ProLevel.PRO_LEVEL_CHOICES[1][0]

  pro_comp[root_pro.id]['qualified'] = True


class Command(BaseCommand):
  help = "Traverse the pro tree and calculate their new levels"

  option_list = BaseCommand.option_list + (
    make_option('-m', '--month',
            type='string',
            dest='month',
            default=None,
            help='Find the orders in this particular month MM/YYYY and save to db. If no date specified use today.'),
    make_option('-b', '--bonus',
            action='store_true',
            dest='bonus',
            default=False,
            help='Calculate monthly bonus'),
    make_option('-l', '--level',
            action='store_true',
            dest='web',
            default=False,
            help='Recalculates the qualification levels monthly'),
    )

  def handle(self, *args, **options):

    # need to go through all orders this month

    if options['month']:
      filter_date = datetime.strptime(options['month'], "%m/%Y").date()
    else:
      filter_date = timezone.now()

    start_datetime = datetime(filter_date.year, filter_date.month, 1, 1, 0, 0)

    # TODO: need to test for pacific time
    # TODO: set the hour to 1 AM
    end_datetime = start_datetime + relativedelta(months=1)

    print "Checking orders from: %s to %s" % (start_datetime, end_datetime)

    pro_comp = {}

    # first need to calculate all personal sales
    for o in Order.objects.filter(order_date__range=[start_datetime, end_datetime]):
      party = o.cart.party
      order_revenue = o.cart.subtotal()

      # after getting tier, add to the table
      if party:
        party_organizer = OrganizedParty.objects.get(party=party)
        pro = party_organizer.pro
      else:
        receiver_profile = o.receiver.get_profile()
        if receiver_profile.is_pro():
          pro = o.receiver
        else:
          # taster and host that have not participated in party
          pro = receiver_profile.current_pro

      if pro.id in pro_comp:
        pro_comp[pro.id]['total_sales'] += order_revenue
      else:
        downline_pros = [uprof.user for uprof in pro.mentor.all()]
        pro_comp[pro.id] = {
          'pro': pro,
          'total_sales': 0,
          'upline': pro.get_profile().mentor,
          'downline': downline_pros,
          'traversed': False,
          'qualified': False,
          'level': ProLevel.PRO_LEVEL_CHOICES[0][0]
        }
        pro_comp[pro.id]['total_sales'] += order_revenue

    # traverse the tree to find the number of active pro's, advanced pro's and elite pro's
    for key, value in pro_comp.items():

      if not value['qualified'] and not value['traversed']:
        # go up the tree
        root_pro = find_root(pro_comp, value['pro'])
        qualify_tree(pro_comp, root_pro)



