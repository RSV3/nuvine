from django.core.management.base import BaseCommand
from optparse import make_option

from django.utils import timezone
from datetime import timedelta, datetime
from main.models import Order, SubscriptionInfo, OrganizedParty
from pro.models import WeeklyCompensation


class Command(BaseCommand):
  help = "Calculate weekly sales"

  option_list = BaseCommand.option_list + (
    make_option('-w', '--week',
      type='string',
      dest='week',
      default=None,
      help='Find the orders in this particular week MM/DD/YYYY and save to db. If no date specified use today.'),
    )

  def handle(self, *args, **options):
    """
        Calculate weekly sales
    """

    print "Options:", options

    if options['week']:
      filter_date = datetime.strptime(options['week'], "%m/%d/%Y").date()
    else:
      filter_date = timezone.now()

    day_of_week = filter_date.weekday()

    if day_of_week == 6:
      # its a sunday, so go back to last sunday
      last_sunday = filter_date - timedelta(days=7)
    else:
      # find starting sunday
      last_sunday = filter_date - timedelta(days=day_of_week + 1)
    start_datetime = datetime(last_sunday.year, last_sunday.month, last_sunday.day, 1, 0, 0)

    # TODO: need to test for pacific time
    # TODO: set the hour to 1 AM
    end_datetime = start_datetime + timedelta(days=7)

    print "Checking orders from: %s to %s" % (start_datetime, end_datetime)

    pro_comp = {}

    # traverse through all orders past week and add to each pro's sales
    for o in Order.objects.filter(order_date__range=[start_datetime, end_datetime]):
      tier = 'A'

      party = o.cart.party
      order_revenue = o.cart.subtotal()

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
        party_organizer = OrganizedParty.objects.get(party=party)
        pro = party_organizer.pro
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
      else:
        # create new pro comp record
        pro_comp[pro.id] = {
          'pro': pro,
          'total_sales': 0,
          'tier_a_sales': 0,
          'tier_b_sales': 0,
          'total_earnings': 0,
          'tier_a_earnings': 0,
          'tier_b_earnings': 0
        }
        pro_comp[pro.id]['total_sales'] += order_revenue
        if tier == 'A':
          pro_comp[pro.id]['tier_a_sales'] += order_revenue
        elif tier == 'B':
          pro_comp[pro.id]['tier_b_sales'] += order_revenue

    for key, value in pro_comp.items():
      comp_record = WeeklyCompensation.objects.filter(pro=value['pro'], start_time=start_datetime)
      if comp_record.exists():
        comp = comp_record[0]
      else:
        comp = WeeklyCompensation(pro=value['pro'])
        # update the compensation
        comp.total_personal_sales = value['total_sales']
        comp.tier_a_personal_sales = value['tier_a_sales']
        comp.tier_b_personal_sales = value['tier_b_sales']
        comp.tier_a_base_earnings = value['tier_a_sales'] * 0.15
        comp.tier_b_base_earnings = value['tier_b_sales'] * 0.08
        comp.total_earnings = comp.tier_a_base_earnings + comp.tier_b_base_earnings
        comp.start_time = start_datetime
        comp.end_time = end_datetime
        comp.save()

    """
      Output calculated weekly compensation
    """
    for comp in WeeklyCompensation.objects.filter(start_time=start_datetime):
      print comp.pro.email, comp.total_personal_sales, comp.tier_a_personal_sales, comp.tier_b_personal_sales
