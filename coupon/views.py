# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse

from coupon.tables import CouponTable
from coupon.models import Coupon
from coupon.forms import CouponForm


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

  form = CouponForm(request.POST or None, instance=coupon)
  data['form'] = form
  data['coupon'] = coupon

  if form.is_valid():
    coupon = form.save()
    return HttpResponseRedirect(reverse('coupon_list'))
  return render(request, 'coupon/coupon_create.html', data)
