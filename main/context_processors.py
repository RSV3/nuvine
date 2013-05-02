from main.models import Cart
from django.conf import settings
from accounts.models import UserProfile
# from django.core.cache import cache


def vinely_user_info(request):

  u = request.user

  data = {}

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
  return data
