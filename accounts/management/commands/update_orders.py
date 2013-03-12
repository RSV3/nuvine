from django.core.management.base import BaseCommand, CommandError
# from optparse import make_option

from django.contrib.auth.models import User
from accounts.models import SubscriptionInfo

from datetime import date
from django.db.models import Q

import logging
log = logging.getLogger(__name__)


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
        log.info("%s %s <%s> has no subscription" % (user.first_name, user.last_name, user.email))
        continue

      if subscription.next_invoice_date == date.today():
        subscription.update_subscription_order()
      else:
        days_left = subscription.next_invoice_date - date.today()
        log.info("%d days left for %s %s <%s> new order" % (days_left.days, user.first_name, user.last_name, user.email))
