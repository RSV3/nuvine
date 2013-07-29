from main.models import Cart
from django.conf import settings
from accounts.models import UserProfile
# from django.core.cache import cache
from django.core.urlresolvers import reverse


def vinely_user_info(request):

  u = request.user

  data = {}
  data['impersonation_mode'] = 'impersonate_id' in request.session
  try:
    profile = u.get_profile()
    if profile.is_pro():
      data["pro"] = True
    if profile.is_host():
      data["host"] = True
    if profile.is_supplier():
      data["supplier"] = True
    if profile.is_taster():
      data["taster"] = True
    if profile.is_pending_pro():
      data["pending_pro"] = True

    if profile.has_personality():
      data['rating_url'] = reverse('general_ratings_overview')
    else:
      # if has previous order:
      # if is taste kit order then must be a VIP member -> show VIP wine rating page
      # else show normal wine rating page
      if profile.has_orders():
        # can only be a VIP taste kit order
        data['rating_url'] = reverse('member_ratings_overview')
  except UserProfile.DoesNotExist:
    pass
  except:
    # anonymous user gets AttributeError
    pass

  data['cart_item_count'] = 0
  if 'cart_id' in request.session:
    try:
      cart = Cart.objects.get(id=request.session['cart_id'])
      data['cart_item_count'] = cart.items.all().count()
    except Cart.DoesNotExist:
      # clear session since db messed up (db must have got cleared)
      del request.session['cart_id']

  data['EMAIL_STATIC_URL'] = settings.EMAIL_STATIC_URL
  data['request'] = request
  data['title'] = 'Vinely'  # set as default title
  return data
