# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
# from django.conf import settings
from django.contrib import messages

from coupon.tables import CouponTable
from coupon.models import Coupon
from coupon.forms import CouponForm

# import time
# import stripe

import logging

logger = logging.getLogger(__name__)


@staff_member_required
def coupon_list(request):
  data = {}
  coupons = Coupon.objects.all()
  data['table'] = CouponTable(coupons)
  return render(request, 'coupon/coupon_list.html', data)


@staff_member_required
def coupon_create(request, coupon_id=None):
  data = {}

  coupon = None
  if coupon_id:
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    messages.warning(request, 'Note that changing the Coupon code will make it unusable for users that might already have the Coupon.')

  form = CouponForm(request.POST or None, instance=coupon)
  data['form'] = form
  data['coupon'] = coupon

  if form.errors.get('__all__'):
    messages.warning(request, form.errors['__all__'])

  if form.is_valid():
    coupon = form.save(commit=False)
    if coupon.duration == Coupon.STRIPE_DURATION_CHOICES[0][0]:
      coupon.max_redemptions = 1
    coupon.save()
    form.save_m2m()

    # NOTE: disabled creating coupon in stripe - can implement the upto 50% limit on stripe
    # so handling this on Vinely

    # coupon = form.save(commit=False)

    # create coupon in stripe as well
    # stripe.api_key = settings.STRIPE_SECRET_CA
    # coupon_config = {
    #     'id': coupon.code,
    #     'currency': 'usd',
    #     'duration': Coupon.STRIPE_DURATION_CHOICES[coupon.duration],
    #     'redeem_by': int(time.mktime(coupon.redeem_by.timetuple())),
    # }
    # if coupon.amount_off > 0:
    #   coupon_config['amount_off'] = coupon.amount_off
    #   # coupon.percent_off = 0
    # else:
    #   coupon_config['percent_off'] = coupon.percent_off
    #   # coupon.amount_off = 0

    # if coupon.duration == Coupon.STRIPE_DURATION_CHOICES[2][0]:
    #   coupon_config['duration_in_months'] = coupon.repeat_duration

    # if coupon.max_redemptions > 0:
    #   coupon_config['max_redemptions'] = coupon.max_redemptions

    # try:
    #   if coupon_id:
    #     stripe_coupon = stripe.Coupon.retrieve(coupon.code)
    #     stripe_coupon.delete()
    # except Exception, e:
    #   pass

    # try:
    #   stripe.Coupon.create(**coupon_config)
    #   coupon.save()
    #   form.save_m2m()
    # except Exception, e:
    #   logger.error(e)
    #   messages.warning(request, 'Error saving the coupon on stripe. %s' % e)
    #   return render(request, 'coupon/coupon_create.html', data)

    # if all is well clear the warning about changing coupon code. Cleared by iterating
    # storage = messages.get_messages(request)
    # for x in storage:
    #   pass

    return HttpResponseRedirect(reverse('coupon_list'))

  return render(request, 'coupon/coupon_create.html', data)
