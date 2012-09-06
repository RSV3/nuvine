from main.models import Cart 
from django.contrib.auth.models import Group

def vinely_user_info(request):

  u = request.user
  
  data = {}

  pro_group = Group.objects.get(name='Vinely Pro')
  soc_group = Group.objects.get(name='Vinely Host')
  sp_group = Group.objects.get(name='Supplier')
  tas_group = Group.objects.get(name='Vinely Taster')
  pending_pro = Group.objects.get(name='Pending Vinely Pro')

  if pro_group in u.groups.all():
    data["pro"] = True
  if soc_group in u.groups.all():
    data["host"] = True
  if sp_group in u.groups.all():
    data["supplier"] = True
  if tas_group in u.groups.all():
    data["taster"] = True 
  if pending_pro in u.groups.all():
    data["pending_pro"] = True

  data['cart_item_count'] = 0
  if 'cart_id' in request.session:
    cart = Cart.objects.get(id=request.session['cart_id'])    
    data['cart_item_count'] = cart.items.all().count()

  return data
