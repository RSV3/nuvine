from django.core.management.base import BaseCommand
from optparse import make_option

from datetime import date, datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from main.models import Order
from accounts.models import SubscriptionInfo, UserProfile

from pro.models import ProLevel, MonthlyQualification, MonthlyBonusCompensation


def find_root(pro_comp, start_pro):
  pro_comp[start_pro.id]['traversed'] = True
  upline_pro = pro_comp[start_pro.id]['upline']
  if upline_pro and pro_comp[upline_pro.id]['traversed'] is False:
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

  if pro_comp[root_pro.id]['qualified']:
    return

  # do a breadth first traverse through the tree
  for downline_pro in pro_comp[root_pro.id]['downline']:
    if pro_comp[downline_pro.id]['downline']:
      # if there are down line pro's then recurse
      print "Checking ROOT: %d and DOWNLINE: %d" % (root_pro.id, downline_pro.id)
      qualify_tree(pro_comp, downline_pro)

    # add up downlines
    downline_total_sales += pro_comp[downline_pro.id]['total_sales']
    if pro_comp[downline_pro.id]['level'] == ProLevel.PRO_LEVEL_CHOICES[1][0]:
      num_active_pros += 1
    elif pro_comp[downline_pro.id]['level'] == ProLevel.PRO_LEVEL_CHOICES[2][0]:
      num_advanced_pros += 1
    elif pro_comp[downline_pro.id]['level'] == ProLevel.PRO_LEVEL_CHOICES[3][0]:
      num_elite_pros += 1

  # sum up all the downline and then qualify root_pro
  root_total_sales = pro_comp[root_pro.id]['total_sales']
  if (root_total_sales >= 10000
              and num_active_pros >= 10
              and num_advanced_pros >= 5
              and num_elite_pros >= 1):
    pro_comp[root_pro.id]['level'] = ProLevel.PRO_LEVEL_CHOICES[4][0]
    new_level = ProLevel(root_pro, ProLevel.PRO_LEVEL_CHOICES[4][0])
    new_level.save()
  elif (root_total_sales >= 7800
              and num_active_pros >= 6
              and num_advanced_pros >= 2):
    pro_comp[root_pro.id]['level'] = ProLevel.PRO_LEVEL_CHOICES[3][0]
    new_level = ProLevel(root_pro, ProLevel.PRO_LEVEL_CHOICES[3][0])
    new_level.save()
  elif (root_total_sales >= 5000
              and num_active_pros >= 3):
    pro_comp[root_pro.id]['level'] = ProLevel.PRO_LEVEL_CHOICES[2][0]
    new_level = ProLevel(root_pro, ProLevel.PRO_LEVEL_CHOICES[2][0])
    new_level.save()
  elif (root_total_sales >= 1500
              and downline_total_sales >= 1200):
    pro_comp[root_pro.id]['level'] = ProLevel.PRO_LEVEL_CHOICES[1][0]
    new_level = ProLevel(root_pro, ProLevel.PRO_LEVEL_CHOICES[1][0])
    new_level.save()

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
            dest='level',
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

    # build the tree
    pro_comp = {}
    for pro in User.objects.all():
      try:
        pro.get_profile()
      except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=pro)
        print "New user profile created for %d, %s" % (pro.id, pro.email)

      if pro.get_profile().is_pro() or pro.get_profile().is_pending_pro():
        downline_pros = []
        for mentee_profile in pro.mentees.all():
          if mentee_profile.user.id != pro.id and (mentee_profile.is_pro() or mentee_profile.is_pending_pro()):
            downline_pros.append(mentee_profile.user)

        # create new pro comp record
        pro_comp[pro.id] = {
          'pro': pro,
          'total_sales': 0,
          'tier_a_sales': 0,
          'tier_b_sales': 0,
          'upline': pro.get_profile().mentor,
          'downline': downline_pros,
          'traversed': False,
          'qualified': False,
          'level': ProLevel.PRO_LEVEL_CHOICES[0][0]
        }

    # first need to calculate all personal sales
    for o in Order.objects.filter(order_date__range=[start_datetime, end_datetime]):
      party = o.cart.party
      order_revenue = o.cart.subtotal()

      # find tier
      tier = 'A'
      for item in o.cart.items.all():
        # need to check if this order is a VIP order, tasting kit and one time order at the party (Tier A)
        if item.frequency != SubscriptionInfo.FREQUENCY_CHOICES[1][0]:
          # it's not a monthly subscription
          tier = 'B'
        else:
          if o.cart.party and o.cart.party.event_date < o.order_date - timedelta(days=7):
            # VIP orders post party or unrelated to party (Tier B)
            tier = 'B'

          # TODO: Missing case where repeated VIP not related to party

      # after getting tier, find out the pro that needs to be credited
      if party:
        # party_organizer = OrganizedParty.objects.get(party=party)
        pro = party.pro
      else:
        receiver_profile = o.receiver.get_profile()
        if receiver_profile.is_pro():
          pro = o.receiver
        else:
          # taster and host that have not participated in party
          pro = receiver_profile.current_pro

      # add to compensation table
      if pro.id in pro_comp:
        pro_comp[pro.id]['total_sales'] += order_revenue
        if tier == 'A':
          pro_comp[pro.id]['tier_a_sales'] += order_revenue
        elif tier == 'B':
          pro_comp[pro.id]['tier_b_sales'] += order_revenue

    # traverse the tree to find the number of active pro's, advanced pro's and elite pro's
    for key, value in pro_comp.items():
      if not value['qualified'] and not value['traversed']:
        # go up the tree
        root_pro = find_root(pro_comp, value['pro'])
        qualify_tree(pro_comp, root_pro)

    # traverse the pro's and generate compensation/bonus report
    if options["bonus"] or options["level"]:
      for key, value in pro_comp.items():
        # find 1st, 2nd, 3rd downline sales

        tier_a_bonus_rate = 0.0
        tier_b_bonus_rate = 0.0
        first_line_bonus_rate = 0.0
        second_line_bonus_rate = 0.0
        third_line_bonus_rate = 0.0
        if pro_comp[key]['level'] == ProLevel.PRO_LEVEL_CHOICES[1][0]:
          first_line_bonus_rate = 0.03
        elif pro_comp[key]['level'] == ProLevel.PRO_LEVEL_CHOICES[2][0]:
          tier_a_bonus_rate = 0.05
          tier_b_bonus_rate = 0.02
          first_line_bonus_rate = 0.04
          second_line_bonus_rate = 0.01
        elif pro_comp[key]['level'] == ProLevel.PRO_LEVEL_CHOICES[3][0]:
          tier_a_bonus_rate = 0.1
          tier_b_bonus_rate = 0.04
          first_line_bonus_rate = 0.05
          second_line_bonus_rate = 0.02
          third_line_bonus_rate = 0.0025
        elif pro_comp[key]['level'] == ProLevel.PRO_LEVEL_CHOICES[4][0]:
          tier_a_bonus_rate = 0.1
          tier_b_bonus_rate = 0.04
          first_line_bonus_rate = 0.05
          second_line_bonus_rate = 0.02
          third_line_bonus_rate = 0.01

        # need to iterate through downlines to calculate total and number of pros
        first_downline_sales = 0.0
        second_downline_sales = 0.0
        third_downline_sales = 0.0
        active_pros = 0
        advanced_pros = 0
        elite_pros = 0
        for first_line in value['downline']:
          first_downline_sales += pro_comp[first_line.id]['total_sales']
          if pro_comp[first_line.id]['level'] == ProLevel.PRO_LEVEL_CHOICES[1][0]:
            active_pros += 1
          elif pro_comp[first_line.id]['level'] == ProLevel.PRO_LEVEL_CHOICES[2][0]:
            advanced_pros += 1
          elif pro_comp[first_line.id]['level'] == ProLevel.PRO_LEVEL_CHOICES[3][0]:
            elite_pros += 1

          # go for second downline
          for second_line in pro_comp[first_line.id]['downline']:
            second_downline_sales += pro_comp[second_line.id]['total_sales']
            for third_line in pro_comp[second_line.id]['downline']:
              third_downline_sales += pro_comp[third_line.id]['total_sales']

        if options["bonus"]:
          bonus, created = MonthlyBonusCompensation.objects.get_or_create(
                                      pro = value['pro'],
                                      start_time = start_datetime,
                                      end_time = end_datetime)
          # just overwrite
          bonus.qualification_level = value['level']
          bonus.total_personal_sales = value['total_sales']
          bonus.tier_a_personal_sales = value['tier_a_sales']
          bonus.tier_b_personal_sales = value['tier_b_sales']
          bonus.total_first_downline_sales = first_downline_sales
          bonus.total_second_downline_sales = second_downline_sales
          bonus.total_third_downline_sales = third_downline_sales
          bonus.tier_a_bonus = value['tier_a_sales']*tier_a_bonus_rate
          bonus.tier_b_bonus = value['tier_b_sales']*tier_b_bonus_rate
          bonus.first_line_bonus = first_downline_sales*first_line_bonus_rate
          bonus.second_line_bonus = second_downline_sales*second_line_bonus_rate
          bonus.third_line_bonus = third_downline_sales*third_line_bonus_rate
          bonus.save()

        if options["level"]:
          qualification, created = MonthlyQualification.objects.get_or_create(
                                        pro = value['pro'],
                                        start_time = start_datetime,
                                        end_time = end_datetime)
          # just overwrite
          qualification.total_personal_sales = value['total_sales']
          qualification.total_sales_1st_line = first_downline_sales
          qualification.active_pros = active_pros
          qualification.advanced_pros = advanced_pros
          qualification.elite_pros = elite_pros
          qualification.qualification_level = value['level']
          qualification.save()

    # print results
    print "%d compensations and %d qualifications calculated" % (
        MonthlyBonusCompensation.objects.filter(start_time=start_datetime).count(),
        MonthlyQualification.objects.filter(start_time=start_datetime).count())
