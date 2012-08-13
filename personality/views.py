# Create your views here.
from urlparse import urlparse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

from main.utils import if_supplier
from personality.models import WineRatingData
from main.models import Order

@login_required
def my_wine_personality(request):
  data = {}

  u = request.user

  data["personality"] = u.get_profile().wine_personality

  return render_to_response("personality/my_wine_personality.html", data, context_instance=RequestContext(request))

@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def personality_details(request, user_id, order_id=None):
  data = {}

  u = request.user

  receiver = get_object_or_404(User, pk=user_id)

  if order_id:
    order = get_object_or_404(Order, order_id=order_id)
    data["order"] = order

  data["personality"] = receiver.get_profile().wine_personality

  rating_data = {}

  try:
    rating_data['wine1'] = WineRatingData.objects.get(user__id=user_id, wine__id=1)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine2'] = WineRatingData.objects.get(user__id=user_id, wine__id=2)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine3'] = WineRatingData.objects.get(user__id=user_id, wine__id=3)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine4'] = WineRatingData.objects.get(user__id=user_id, wine__id=4)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine5'] = WineRatingData.objects.get(user__id=user_id, wine__id=5)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine6'] = WineRatingData.objects.get(user__id=user_id, wine__id=6)
  except WineRatingData.DoesNotExist:
    pass

  data["rating_data"] = rating_data

  return render_to_response("personality/personality_details.html", data, context_instance=RequestContext(request))

