# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q

from main.models import Party, PartyInvite, MySocializer, Product, LineItem, Cart, SubscriptionInfo, \
                        CustomizeOrder, Order, EngagementInterest, OrganizedParty
from personality.models import Wine, WineTaste, GeneralTaste
from accounts.models import VerificationQueue

from main.forms import ContactRequestForm, PartyCreateForm, PartyInviteTasterForm, VinelyProSignupForm, \
                        AddWineToCartForm, AddTastingKitToCartForm, CustomizeOrderForm, ShippingForm, \
                        CustomizeInvitationForm, OrderFulfillForm

from accounts.forms import CreditCardForm, PaymentForm

from accounts.utils import send_verification_email, send_new_invitation_email, send_new_party_email
from main.utils import send_order_confirmation_email, send_host_vinely_party_email, send_new_party_scheduled_email, \
                        distribute_party_invites_email, send_party_invitation_email, UTC, \
                        send_contact_request_email, send_order_shipped_email, if_supplier, if_pro


import json, uuid
from urlparse import urlparse
from datetime import date, datetime, timedelta


def suppliers_only(request):
  """
    Redirected to this page when one is trying to access only supplier only features
  """
  data = {}
  data["message"] = "Only suppliers are allowed to access this page"
  return render_to_response("403.html", data, context_instance=RequestContext(request))

def pros_only(request):
  """
    Redirected to this page when one is trying to access only pro only features
  """
  data = {}
  data["message"] = "Only Vinely Pros are allowed to access this page"
  return render_to_response("403.html", data, context_instance=RequestContext(request))

@login_required
def home(request):
  data = {}

  u = request.user

  if request.user.is_authenticated():
    data["output"] = "User is authenticated"

    pro_group = Group.objects.get(name='Vinely Pro')
    soc_group = Group.objects.get(name='Vinely Socializer')
    sp_group = Group.objects.get(name='Supplier')
    tas_group = Group.objects.get(name='Vinely Taster')

    if pro_group in u.groups.all():
      data["pro"] = True
    if soc_group in u.groups.all():
      data["socializer"] = True
    if sp_group in u.groups.all():
      data["supplier"] = True
    if tas_group in u.groups.all():
      data["taster"] = True
      data["invites"] = PartyInvite.objects.filter(invitee=u) 
      invites = PartyInvite.objects.filter(invitee=u).order_by('-party__event_date')
      if invites.exists():
        data['party_date'] = invites[0].party.event_date

    profile = u.get_profile()
    if profile.wine_personality:
      data['wine_personality'] = profile.wine_personality 
    else:
      data['wine_personality'] = False

    data['questionnaire_completed'] = WineTaste.objects.filter(user=u).exists() and GeneralTaste.objects.filter(user=u).exists()

    # TODO: if there are orders pending
    data['pending_ratings'] = False

    # go to home page

    # if user is Vinely Pro
    # - be able to add new users and send them e-mail 
    # - see users registered at a party
    # - add a new socializer
    # - be able to order for a user
    # - be able to enter ratings for a user

    # if user is socializer
    # - list of parties (aggregate view of orders placed)
    # - list of Vinely Tasters in each party (aggregate of what each Vinely Taster ordered)
    # - see orders placed by each Vinely Taster in detail 
    # - create party
    # - invite Vinely Tasters

    # if user is Vinely Taster
    # - my wine personality
    # - order wine

    # if user is admin
  else:
    data["output"] = "User is not authenticated"
    return HttpResponseRedirect(reverse("landing_page"))

  return render_to_response("main/home.html", data, context_instance=RequestContext(request))

def our_story(request):
  """

  """

  data = {}

  data['our_story_menu'] = True

  return render_to_response("main/our_story.html", data, context_instance=RequestContext(request))

def get_started(request):
  """
    Get started
  """

  data = {}

  u = request.user

  pro_group = Group.objects.get(name="Vinely Pro")
  soc_group = Group.objects.get(name="Vinely Socializer")
  if u.is_authenticated():
    if pro_group in u.groups.all(): 
      data["already_pro"] = True
    if soc_group in u.groups.all():
      data["already_socializer"] = True

  data['get_started_menu'] = True

  return render_to_response("main/get_started.html", data, context_instance=RequestContext(request))

def contact_us(request):
  """

  """

  data = {}

  if request.method == "POST":
    form = ContactRequestForm(request.POST)
    if form.is_valid():
      contact_request = form.save()
      send_contact_request_email(request, contact_request)
      return render_to_response("main/thankyou_contact.html", data, context_instance=RequestContext(request))
  else:
    form = ContactRequestForm()

  data["form"] = form

  return render_to_response("main/contact_us.html", data, context_instance=RequestContext(request))

@login_required
def become_vip(request):
  """
    TODO: what is to become VIP
  """

  data = {}

  return render_to_response("main/become_vip.html", data, context_instance=RequestContext(request))

@login_required
def rate_wines(request):
  """
    Rate wines
  """
  data = {}

  data['rate_wines_menu'] = True
  return render_to_response("main/rate_wines.html", data, context_instance=RequestContext(request))

@login_required
def host_vinely_party(request):
  """
    Host your own Vinely party
  """
  
  data = {}

  # sends a notification to the Vinely Pro so this user can be upgraded to Vinely Host
  message_body = send_host_vinely_party_email(request)

  data["message"] = message_body

  return render_to_response("main/host_vinely_party.html", data, context_instance=RequestContext(request))

def how_it_works(request):
  """

  """

  data = {}

  data["how_it_works_menu"] = True

  return render_to_response("main/how_it_works.html", data, context_instance=RequestContext(request))

def start_order(request, receiver_id=None, party_id=None):
  """
    Show wine order page

    :param receiver_id: the user id of the user who's order is being fulfilled
                      for example, when a Vinely Pro enters rating data and continues an order
                      for a guest, the guest user id is the receiver_id
  """
  data = {}
  #: receiver's wine personality, or current user's wine personality
  personality = None

  u = request.user

  if receiver_id:
    # ordering for a particular user
    request.session['receiver_id'] = int(receiver_id)
  if party_id:
    # ordering from a particular party
    request.session['party_id'] = int(party_id)

  data["your_personality"] = "Unidentified"
  if receiver_id:
    receiver = User.objects.get(id=receiver_id)
    personality = receiver.get_profile().wine_personality
  elif u.is_authenticated():
    # ordering for oneself
    personality = u.get_profile().wine_personality
  if personality:
    data["your_personality"] = personality.name

  # filter only wine packages
  products = Product.objects.filter(category=Product.PRODUCT_TYPE[1][0])

  data["products"] = products
  data["shop_menu"] = True

  return render_to_response("main/start_order.html", data, context_instance=RequestContext(request))

@login_required
def order_tasting_kit(request):
  """

    Order tasting kit

  """
  data = {}

  form = SimpleItemOrderForm(request.POST or None)
  if form.is_valid():
    # need to be able to add item to cart
    item = form.save()
    return HttpResponseRedirect(reverse("main.views.cart"))

  tasting_kits = Product.objects.filter(category="Tasting Kit")
  data = {
        'item_name': tasting_kit.name,
        'item_description': tasting_kit.description,
        'item_price': tasting_kit.price
      }
  data["form"] = form
  data["shop_menu"] = True
  return render_to_response("main/order_tasting_kit.html", data, context_instance=RequestContext(request))


def cart_add_tasting_kit(request):
  """
    
    Add tasting kit to cart

    submit goes to checkout
  """
  data = {}

  u = request.user

  party = None
  if 'party_id' in request.session:
    party = Party.objects.get(id=request.session['party_id'])

  form = AddTastingKitToCartForm(request.POST or None)

  if form.is_valid():
    # add line item to cart
    item = form.save()
    if 'cart_id' in request.session:
      cart = Cart.objects.get(id=request.session['cart_id'])
      cart.items.add(item)
      cart.save()
    else:
      # create new cart, for currently active user
      if u.is_authenticated():
        cart = Cart(user=u)
      else:
        # anonymous cart
        cart = Cart()
      cart.save()
      cart.items.add(item)
      request.session['cart_id'] = cart.id

    # udpate cart status
    if party:
      cart.party = party
    cart.status = Cart.CART_STATUS_CHOICES[1][0] 
    cart.adds += 1
    cart.save()

    return HttpResponseRedirect(reverse("cart"))

  if Product.objects.filter(category=Product.PRODUCT_TYPE[0][0]).exists():
    product = Product.objects.filter(category=Product.PRODUCT_TYPE[0][0])[0]
    data["product"] = product
    form.initial = {'product': product, 'total_price': product.unit_price}
    data["form"] = form
    
  data["shop_menu"] = True

  return render_to_response("main/cart_add_tasting_kit.html", data, context_instance=RequestContext(request))

def cart_add_wine(request, level="basic"):
  """
    
    Add item to cart

    submit goes to checkout
  """
  data = {}

  u = request.user

  party = None
  if 'party_id' in request.session:
    party = Party.objects.get(id=request.session['party_id'])

  # TODO: check user personality and select the frequency recommendation and case size

  form = AddWineToCartForm(request.POST or None)

  if form.is_valid():
    # add line item to cart
    item = form.save()
    if 'cart_id' in request.session:
      cart = Cart.objects.get(id=request.session['cart_id'])
      cart.items.add(item)
      cart.save()
    else:
      # create new cart
      if u.is_authenticated():
        cart = Cart(user=u)
      else:
        # anonymous cart
        cart = Cart()
      cart.save()
      cart.items.add(item)
      request.session['cart_id'] = cart.id

    # udpate cart status
    if party:
      cart.party = party
    cart.status = Cart.CART_STATUS_CHOICES[1][0] 
    cart.adds += 1
    cart.save()

    data["shop_menu"] = True
    return HttpResponseRedirect(reverse("cart"))

  # big image of wine
  # TODO: need to check wine personality and choose the right product
  if level == "basic":
    product = Product.objects.get(name="Basic Vinely Recommendation")
  elif level == "classic":
    product = Product.objects.get(name="Classic Vinely Recommendation")
  elif level == "divine":
    product = Product.objects.get(name="Divine Vinely Recommendation")
  elif level == "x":
    # not a valid product
    raise Http404

  data["product"] = product

  form.initial = {'level': level, 
                'total_price': product.unit_price,
                'product': product}
  data["form"] = form
  data["level"] = level

  data["shop_menu"] = True
  return render_to_response("main/cart_add_wine.html", data, context_instance=RequestContext(request))

def cart(request):
  """
    
    Show items in cart, have a link to go back to start_order to order more

    submit goes to checkout
  """
  data = {}

  try:
    cart_id = request.session['cart_id']
    cart = Cart.objects.get(id=cart_id) 
    cart.views += 1
    cart.save()
    data["items"] = cart.items.all()
    data["cart"] = cart
  except KeyError:
    # cart is empty
    data["items"] = []

  data["shop_menu"] = True

  return render_to_response("main/cart.html", data, context_instance=RequestContext(request))

def cart_remove_item(request, cart_id, item_id):
  """
    Delete an item from cart
  """

  data = {}

  cart = Cart.objects.get(id=cart_id)
  item = LineItem.objects.get(id=item_id)
  
  cart.items.remove(item)

  # track cart activity
  cart.removes += 1
  cart.save()

  data["shop_menu"] = True

  return HttpResponseRedirect(request.GET.get("next"))

def customize_checkout(request):
  """
    Customize checkout to specify the receiver's preferences on wine mix and sparkling
    The page allows a Vinely Pro to set settings for a guest who's order is being
    created or if a guest is not assigned, then CustomizeOrder is created for the current
    logged in user and assigned to the receiver when shipping address is created.
  """

  data = {}

  u = request.user

  receiver = None
  if 'receiver_id' in request.session:
    receiver = User.objects.get(id=request.session['receiver_id'])

  if u.is_authenticated():
    try:
      if receiver:
        custom = CustomizeOrder.objects.get(user=receiver)
      else:
        custom = CustomizeOrder.objects.get(user=u)
    except CustomizeOrder.DoesNotExist:
      # continue to show customization form which will be filled in with current user's customization initially
      custom = None

  form = CustomizeOrderForm(request.POST or None, instance=custom)
  if form.is_valid():
    custom = form.save(commit=False)
    if custom.user is None:
      if receiver:
        custom.user = receiver
      else:
        custom.user = u
    custom.save()

    cart = Cart.objects.get(id=request.session['cart_id']) 
    cart.status = Cart.CART_STATUS_CHOICES[2][0] 
    cart.save()

    data["shop_menu"] = True

    return HttpResponseRedirect(reverse('main.views.edit_shipping_address'))
      
  if custom is None:
    form.initial = {'wine_mix': 0, 'sparkling': 1}
  data['form'] = form
  data["shop_menu"] = True

  return render_to_response("main/customize_checkout.html", data, context_instance=RequestContext(request))

@login_required
def place_order(request):
  """
    This page allows you to review the order and finalize the order
 
  """
  data = {}
  u = request.user

  data["your_personality"] = "Moxie"

  # set this to use in edit_shipping_address and edit_credit_card to indicate that
  # order has been reviewed 
  request.session['ordering'] = True 
  
  if 'cart_id' in request.session:
    try:
      cart = Cart.objects.get(id=request.session['cart_id'])
    except Cart.DoesNotExist:
      raise Http404

    if 'receiver_id' in request.session:
      receiver = User.objects.get(id=request.session['receiver_id'])
      profile = receiver.get_profile()
    else:
      raise Http404

    if request.method == "POST": 
      # finalize order

      if 'order_id' in request.session:
        # existing order id, in case user submits multiple times
        order_id = request.session['order_id']
      else:
        # new order id
        order_id = str(uuid.uuid4())
        request.session['order_id'] = order_id

      try:
        # create order: existing cart
        order = Order.objects.get(cart=cart)
        order.order_id = order_id 
        if u.is_authenticated():
          order.ordered_by = u
        order.receiver = receiver
      except Order.DoesNotExist:
        # create new order for this cart
        order = Order(ordered_by=u, receiver=receiver, order_id=order_id, cart=cart)

      # save credit card and shipping address in the order
      order.credit_card = profile.credit_card
      order.shipping_address = profile.shipping_address
      order.save()

      cart.status = Cart.CART_STATUS_CHOICES[5][0] 
      cart.save()

      # save cart to order
      data["shop_menu"] = True
      return HttpResponseRedirect(reverse("order_complete", args=[order_id]))

    else:
      # review what you have ordered
      data["items"] = cart.items.all()
      data["cart" ] = cart

      # record cart views
      cart.views += 1
      cart.save()

      data["receiver"] = receiver
      data["credit_card"] = profile.credit_card 
      data["shipping_address"] = profile.shipping_address

      data["shop_menu"] = True
      return render_to_response("main/place_order.html", data, context_instance=RequestContext(request))
  else:
    messages.error(request, 'Your session expired, please start ordering again.')
    data["shop_menu"] = True
    return HttpResponseRedirect(reverse("start_order"))

@login_required
def order_complete(request, order_id):

  data = {}

  u = request.user

  # remove session information if it exists
  if 'ordering' in request.session:
    del request.session['ordering']
  if 'order_id' in request.session:
    del request.session['order_id']
  if 'cart_id' in request.session:
    del request.session['cart_id']
  if 'receiver_id' in request.session:
    del request.session['receiver_id']

  try:
    order = Order.objects.get(order_id=order_id)
  except Order.DoesNotExist:
    raise Http404

  if order.fulfill_status == 0:
    # update subscription information if new order
    for item in order.cart.items.all():
      # check if item contains subscription
      if item.price_category in range(5, 11):
        subscription, created = SubscriptionInfo.objects.get_or_create(user=order.receiver)
        subscription.quantity = item.price_category
        subscription.frequency = item.frequency 
        subscription.save()

  if order.ordered_by == u or order.receiver == u:
    # only viewable by one who ordered or one who's receiving

    data["order"] = order

    cart = order.cart
    data["cart"] = cart
    data["items"] = cart.items.all()

    # need to send e-mail
    send_order_confirmation_email(request, order_id)

    data["shop_menu"] = True
    return render_to_response("main/order_complete.html", data, context_instance=RequestContext(request))
  else:
    raise PermissionDenied

@login_required
def order_history(request):

  data = {}
  u = request.user

  data["orders"] = Order.objects.filter( Q( ordered_by=u ) | Q( receiver=u ) )

  data["shop_menu"] = True
  return render_to_response("main/order_history.html", data, context_instance=RequestContext(request))



@login_required
def parties(request):
  """
    Show list of parties
  """
  data = {}

  data["parties"] = Party.objects.all()
  data["party_invites"] = PartyInvite.objects.values('party').annotate(num_invites=Count('invitee'))

  return render_to_response("main/parties.html", data, context_instance=RequestContext(request))

@login_required
def tag(request):
  """ 
    Tag a member with particular term 
    - people can edit tags 
    - ajax call
    - log those people who added those tags
  """
  data = {}

  data["result"] = "tagging successful"

  return HttpResponse(json.dumps(data), mimetype="application/json") 


@login_required
def party_list(request):
  """
    Show upcoming and past parties
  """

  u = request.user

  data = {}

  pro_group = Group.objects.get(name="Vinely Pro")
  soc_group = Group.objects.get(name="Vinely Socializer")
  sp_group = Group.objects.get(name='Supplier')
  tas_group = Group.objects.get(name='Vinely Taster')

  if pro_group in u.groups.all():
    data["pro"] = True
  if soc_group in u.groups.all():
    data["socializer"] = True
  if sp_group in u.groups.all():
    data["supplier"] = True
  if tas_group in u.groups.all():
    data["taster"] = True

  today = datetime.now(tz=UTC())

  if (pro_group in u.groups.all()):
    # need to filter to parties that a particular user manages
    my_socializers = MySocializer.objects.filter(pro=u).values_list('socializer', flat=True)
    data['parties'] = Party.objects.filter(socializer__in=my_socializers, event_date__gte=today)
    data['past_parties'] = Party.objects.filter(socializer__in=my_socializers, event_date__lt=today)
  elif (soc_group in u.groups.all()):
    data['parties'] = Party.objects.filter(socializer=u, event_date__gte=today)
    data['past_parties'] = Party.objects.filter(socializer=u, event_date__lt=today)
  elif (tas_group in u.groups.all()):
    for inv in PartyInvite.objects.filter(invitee=u):
      data['parties'] = []
      data['past_parties'] = []
      if inv.party.event_date < today:
        data['past_parties'].append(inv.party)
      else:
        data['parties'].append(inv.party)
  else:
    raise PermissionDenied 

  data["parties_menu"] = True

  return render_to_response("main/party_list.html", data, context_instance=RequestContext(request))

@login_required
def party_add(request):
  """
    Add a new party
  """
  data = {}

  u = request.user

  pro_group = Group.objects.get(name="Vinely Pro")
  soc_group = Group.objects.get(name="Vinely Socializer")
  sp_group = Group.objects.get(name='Supplier')
  tas_group = Group.objects.get(name='Vinely Taster')

  if pro_group in u.groups.all():
    data["pro"] = True
  if soc_group in u.groups.all():
    data["socializer"] = True
  if sp_group in u.groups.all():
    data["supplier"] = True
  if tas_group in u.groups.all():
    data["taster"] = True

  data["no_perms"] = False
  if pro_group not in u.groups.all():
    # if not a Vinely Pro, one does not have permissions
    data["no_perms"] = True
    return render_to_response("main/party_add.html", data, context_instance=RequestContext(request))

  if request.method == "POST":
    form = PartyCreateForm(request.POST)
    if form.is_valid():

      new_party = form.save()
      new_socializer = new_party.socializer

      # map socializer to a pro
      my_socializers, created = MySocializer.objects.get_or_create(pro=u, socializer=new_socializer)
      proy_parties, created = OrganizedParty.objects.get_or_create(pro=u, party=new_party)

      if not new_socializer.is_active:
        # new socializer, so send password and invitation
        temp_password = User.objects.make_random_password()
        new_socializer.set_password(temp_password)
        new_socializer.save()

        verification_code = str(uuid.uuid4())
        vque = VerificationQueue(user=new_socializer, verification_code=verification_code)
        vque.save()

        # send an invitation e-mail if new socializer created 
        send_new_party_email(request, verification_code, temp_password, new_socializer.email)
      else:
        # existing socializer needs to notified that party has been arranged
        send_new_party_scheduled_email(request, new_party)

      messages.success(request, "Party (%s) has been successfully scheduled." % (new_party.title, ))

      data["parties_menu"] = True
      # go to party list page
      return HttpResponseRedirect(reverse("party_list"))
  else:
    # if the current user is socializer, display Vinely Pro
    if "socializer" in data and data["socializer"]:
      pros = MySocializer.objects.filter(socializer=u)
      if pros.exists():
        pro = pros[0].pro
        data["my_pro"] = pro 
        send_host_vinely_party_email(request, pro)
      else:
        send_host_vinely_party_email(request)

    # if the current user is Vinely Taster, display Vinely Pro
    if "taster" in data and data["taster"]:
      # find the latest party that guest attended and then through the socializer to find the Vinely Pro
      party_invites = PartyInvite.objects.filter(invitee=u).order_by('-party__event_date')
      if party_invites.exists():
        party = party_invites[0].party
        primary_socializer = party.socializer
        pros = MySocializer.objects.filter(socializer=primary_socializer)
        if pros.exists():
          pro = pros[0].pro
          data["my_pro"] = pro 
          send_host_vinely_party_email(request, pro)
        else:
          # if no pro found, just e-mail sales
          send_host_vinely_party_email(request)
      else:
        # if no previous party found, just e-mail sales
        send_host_vinely_party_email(request)

    initial_data = {'event_day': datetime.today().strftime("%m/%d/%Y")}
    form = PartyCreateForm(initial=initial_data)
    soc_group = Group.objects.get(name="Vinely Socializer")
    # need to figure out socializers filtered by Vinely Pro
    form.fields['socializer'].choices = [(mysocializer.socializer.id, mysocializer.socializer.email) for mysocializer in MySocializer.objects.filter(pro=u)]

  data["form"] = form
  data["parties_menu"] = True

  return render_to_response("main/party_add.html", data, context_instance=RequestContext(request))

@login_required
def party_details(request, party_id):
  """
    Get details of a party, view party guests and inform, invite new guests

  """

  data = {}

  u = request.user

  party = None
  if party_id and int(party_id) != 0:
    party = get_object_or_404(Party, pk=party_id)

  pro_group = Group.objects.get(name="Vinely Pro")
  soc_group = Group.objects.get(name="Vinely Socializer")
  sp_group = Group.objects.get(name='Supplier')
  tas_group = Group.objects.get(name='Vinely Taster')

  if pro_group in u.groups.all():
    data["pro"] = True
  if soc_group in u.groups.all():
    data["socializer"] = True
  if sp_group in u.groups.all():
    data["supplier"] = True
  if tas_group in u.groups.all():
    data["taster"] = True

  invitees = PartyInvite.objects.filter(party=party)

  data["party"] = party
  data["invitees"] = invitees

  # TODO: might have to fix this and set Party to have a particular pro
  my_socializers = MySocializer.objects.filter(socializer=party.socializer).order_by("-timestamp")
  data["pro_user"] = my_socializers[0].pro
  data["parties_menu"] = True

  return render_to_response("main/party_details.html", data, context_instance=RequestContext(request))

@login_required
def party_taster_list(request, party_id):
  """
    Show Vinely Tasters of a party
  """

  data = {}

  u = request.user

  party = None
  if party_id and int(party_id) != 0:
    party = get_object_or_404(Party, pk=party_id)

  pro_group = Group.objects.get(name="Vinely Pro")
  soc_group = Group.objects.get(name="Vinely Socializer")
  sp_group = Group.objects.get(name='Supplier')
  tas_group = Group.objects.get(name='Vinely Taster')

  if pro_group in u.groups.all():
    data["pro"] = True
  if soc_group in u.groups.all():
    data["socializer"] = True
  if sp_group in u.groups.all():
    data["supplier"] = True
  if tas_group in u.groups.all():
    data["taster"] = True

  invitees = PartyInvite.objects.filter(party=party)

  data["party"] = party
  data["invitees"] = invitees
  data["parties_menu"] = True

  return render_to_response("main/party_taster_list.html", data, context_instance=RequestContext(request))

@login_required
def party_taster_invite(request, party_id=0):
  """
    Invite a new Vinely Taster to a party 

      - only allow socializer or Vinely Pro to add
      - need to track who added and make sure the Vinely Taster is linked to that pro or socializer

  """
  data = {}

  u = request.user

  if Party.objects.all().count() == 0:
    data["no_parties"] = True
    return render_to_response("main/party_taster_invite.html", data, context_instance=RequestContext(request))

  pro_group = Group.objects.get(name='Vinely Pro')
  soc_group = Group.objects.get(name='Vinely Socializer')
  tas_group = Group.objects.get(name='Vinely Taster')

  if pro_group in u.groups.all():
    data["pro"] = True
  if soc_group in u.groups.all():
    data["socializer"] = True
  if tas_group in u.groups.all():
    data["taster"] = True

  party = None
  if int(party_id) != 0:
    party = get_object_or_404(Party, pk=party_id)

    if tas_group in u.groups.all():
      try:
        # Vinely Taster must have been already invited to invite more
        invite = PartyInvite.objects.get(party=party, invitee=u)
      except PartyInvite.DoesNotExist:
        raise PermissionDenied

  if pro_group in u.groups.all() or soc_group in u.groups.all() or tas_group in u.groups.all(): 
    if request.method == "POST":
      form = PartyInviteTasterForm(request.POST)
      if form.is_valid():
        new_invite = form.save()
        new_invite.invited_by = u
        new_invite.save()

        new_invitee = new_invite.invitee

        if new_invitee.is_active is False:
          # new user created through party invitation
          temp_password = User.objects.make_random_password()
          new_invitee.set_password(temp_password)
          new_invitee.save()

          verification_code = str(uuid.uuid4())
          vque = VerificationQueue(user=new_invitee, verification_code=verification_code)
          vque.save()

          # send an invitation e-mail, new user created 
          send_new_invitation_email(request, verification_code, temp_password, new_invite)
          
        # removed following lines since invitation get sent in a batch from the UI
        #else:
        #  send_party_invitation_email(request, new_invite)

        messages.success(request, '%s %s (%s) has been invited to the party.' % ( new_invitee.first_name, new_invitee.last_name, new_invitee.email ))


        data["parties_menu"] = True
        return HttpResponseRedirect(reverse("party_details", args=[new_invite.party.id]))
    else:
      # if request is GET
      if int(party_id) == 0:
        # unspecified party
        form = PartyInviteTasterForm()
      else:
        # specified party
        initial_data = {'party': party}
        form =  PartyInviteTasterForm(initial=initial_data)

    if tas_group in u.groups.all():
      today = datetime.now(tz=UTC())
      parties = []
      for inv in PartyInvite.objects.filter(invitee=u, party__event_date__gt=today):
        parties.append((inv.party.id, inv.party.title))
      form.fields['party'].choices = parties 
    elif soc_group in u.groups.all():
      today = datetime.now(tz=UTC())
      parties = Party.objects.filter(socializer=u, event_date__gt=today)
      form.fields['party'].queryset = parties 
    elif pro_group in u.groups.all():
      my_socializers = MySocializer.objects.filter(pro=u)
      my_socializer_list = []
      for my_socializer in my_socializers:
        my_socializer_list.append(my_socializer.socializer)
      parties = Party.objects.filter(socializer__in=my_socializer_list)
      form.fields['party'].queryset = parties

    data["form"] = form
    data["party"] = party
    data["parties_menu"] = True

    return render_to_response("main/party_taster_invite.html", data, context_instance=RequestContext(request))
  else:
    raise PermissionDenied 

@login_required
def party_rsvp(request, party_id, response=None):

  data = {}
  u = request.user

  party = get_object_or_404(Party, pk=party_id) 
  try:
    invite = PartyInvite.objects.get(party=party, invitee=u)
  except PartyInvite.DoesNotExist:
    raise Http404

  if response:
    invite.response = int(response)
    invite.save()

  invitees = PartyInvite.objects.filter(party=party).exclude(invitee=u)
  data['questionnaire_completed'] = WineTaste.objects.filter(user=u).exists() and GeneralTaste.objects.filter(user=u).exists()
  data["party"] = party
  data["invitees"] = invitees
  data["invite"] = invite
  data["parties_menu"] = True
  invitations = party.invitationsent_set.all().order_by("-timestamp")
  if invitations.exists():
    data["custom_message"] = invitations[0].custom_message

  return render_to_response("main/party_rsvp.html", data, context_instance=RequestContext(request))

@login_required
def party_customize_invite(request):
  """
    Customize invitations to those people
  """

  # TODO: show that the following invitation will be sent
  data = {}

  if request.method == 'POST':
    guests = request.POST.getlist('guests')
    party = Party.objects.get(id=request.POST.get('party'))
    print "Selected guests:", guests

    form = CustomizeInvitationForm()
    form.initial = {'party': party}
    data["party"] = party
    data["guests"] = guests 
    data["form"] = form
    data["guest_count"] = len(guests)
    data["parties_menu"] = True

    return render_to_response("main/party_customize_invite.html", data, context_instance=RequestContext(request))
  else:
    return PermissionDenied

@login_required
def party_send_invites(request):
  """
    Preview invitation or send the invites
  """

  data = {}

  # send invitation 
  form = CustomizeInvitationForm(request.POST or None)
  if form.is_valid():
    if form.cleaned_data['preview']:
      invitation_sent = form.save(commit=False)
      party = invitation_sent.party
      data["preview"] = True
      data["party"] = party
      data["guests"] = request.POST.getlist("guests")
    else:
      invitation_sent = form.save()

      party = invitation_sent.party

      # send e-mails
      distribute_party_invites_email(request, invitation_sent)

      messages.success(request, "Invitations have been sent to your guests.")
      data["parties_menu"] = True

      return HttpResponseRedirect(reverse("main.views.party_details", args=[party.id]))

  data["form"] = form
  data["parties_menu"] = True

  return render_to_response("main/party_invite_preview.html", data, context_instance=RequestContext(request))

@login_required
@user_passes_test(if_pro, login_url="/pros/only/")
def dashboard(request):
  data = {}

  data["dashboard_menu"] = True

  return render_to_response("main/dashboard.html", data, context_instance=RequestContext(request))

################################################################################
#
# Supplier views
#
################################################################################

@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def supplier_party_list(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data["supplier"] = True
  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def supplier_party_orders(request, party_id):
  """
    Show orders from a particular party for the supplier 

  """
  data = {}

  data["supplier"] = True
  data['party'] = Party.objects.get(id=party_id)

  return render_to_response("main/supplier_party_orders.html", data, context_instance=RequestContext(request))

@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def supplier_pending_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data["supplier"] = True
  data["orders"] = Order.objects.filter(fulfill_status__lt=Order.FULFILL_CHOICES[6][0])

  return render_to_response("main/supplier_pending_orders.html", data, context_instance=RequestContext(request))

@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def supplier_fulfilled_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data["supplier"] = True
  data["orders"] = Order.objects.filter(fulfill_status__gte=Order.FULFILL_CHOICES[6][0])

  return render_to_response("main/supplier_fulfilled_orders.html", data, context_instance=RequestContext(request))

@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def supplier_all_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data["supplier"] = True
  data['orders'] = Order.objects.all()

  return render_to_response("main/supplier_all_orders.html", data, context_instance=RequestContext(request))

@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def supplier_edit_order(request, order_id):
  """
    Update order status or add tracking number
  """

  data = {}

  u = request.user

  try:
    order = Order.objects.get(order_id=order_id)
  except Order.DoesNotExist:
    raise Http404

  form = OrderFulfillForm(request.POST or None, instance=order)
  if form.is_valid():
    # save the tracking number or fulfill status
    order = form.save()
    if order.fulfill_status == 6:
      send_order_shipped_email(request, order)

    messages.success(request, "Fulfill status has been updated.")
      
  data["order"] = order

  cart = order.cart
  data["cart"] = cart
  data["items"] = cart.items.all()
  data["form"] = form
  data["order_id"] = order_id

  receiver = order.receiver
  data["personality"] = receiver.get_profile().wine_personality

  try:
    data["customization"] = CustomizeOrder.objects.get(user=order.receiver)
  except CustomizeOrder.DoesNotExist:
    pass

  return render_to_response("main/supplier_edit_order.html", data, context_instance=RequestContext(request))

def edit_shipping_address(request):
  """
    Update or add shipping address
    Receiving user is created if she doesn't exist
    Cart is assigned the current party or the latest party that the receiver participated

    pre condition: cart has been created

  """
  data = {}

  # prepopulate with shipping address

  u = request.user

  receiver = None
  if u.is_anonymous():
    form = ShippingForm(request.POST or None)
  else:
    if 'receiver_id' in request.session:
      receiver = User.objects.get(id=request.session['receiver_id'])
      print "Receiver's email: %s"%receiver.email
    else:
      receiver = u
    form = ShippingForm(request.POST or None, instance=receiver)

  if form.is_valid():
    receiver = form.save()

    # update the receiver user
    request.session['receiver_id'] = receiver.id

    # check if customization exists, if not we need to assign it from the one who's ordering now
    try:
      CustomizeOrder.objects.get(user=receiver)
    except CustomizeOrder.DoesNotExist:
      # customization that current user filled out
      current_customization = CustomizeOrder.objects.get(user=u)
      new_customization = CustomizeOrder(user=receiver, wine_mix=current_customization.wine_mix, sparkling=current_customization.sparkling)
      new_customization.save()

    if receiver.is_active is False: 
      # if new receiving user created.  happens when receiver never attended a party
      role = Group.objects.get(name="Vinely Taster")
      receiver.groups.add(Group.objects.get(name=role))

      temp_password = User.objects.make_random_password()
      receiver.set_password(temp_password)
      receiver.save()

      verification_code = str(uuid.uuid4())
      vque = VerificationQueue(user=receiver, verification_code=verification_code)
      vque.save()

      # send out verification e-mail, create a verification code
      send_verification_email(request, verification_code, temp_password, receiver.email)

      if not u.is_authenticated():
        # if no user is currently authenticated
        # authenticate the new user and replace with the logged in user
        u = authenticate(email=receiver.email, password=temp_password)

        # return authenticated user
        if u is not None:
          login(request, u)
        else:
          raise Http500

    if u.is_authenticated() and u != receiver: 
      # if receiver is already an active user and receiver is not currently logged in user
      receiver_profile = receiver.get_profile()
      profile = u.get_profile()
      profile.shipping_address = receiver_profile.shipping_address
      profile.shipping_addresses.add(receiver_profile.shipping_address)
      profile.save()

    if 'ordering' in request.session and request.session['ordering']:
      # only happens when user decided to edit the shipping address
      data["shop_menu"] = True
      return HttpResponseRedirect(reverse("place_order"))
    else:
      # update cart status
      cart = Cart.objects.get(id=request.session['cart_id'])
      cart.status = Cart.CART_STATUS_CHOICES[3][0]
      cart.save()

      if cart.party is None:
        if 'party_id' in request.session:
          party = Party.objects.get(id=request.session['party_id'])
        else:
          # find the party this receiver has participated
          recent_invites = PartyInvite.objects.filter(invitee=receiver).order_by('-invited_timestamp')
          if recent_invites.exists():
            party = recent_invites[0].party

        if party:
          # assign cart to a party
          cart.party = party
          cart.save()

      data["shop_menu"] = True
      return HttpResponseRedirect(reverse("edit_credit_card"))

  # display form: populate with initial data if user is authenticated
  initial_data = {}
  if receiver:
    initial_data = {'first_name': receiver.first_name, 'last_name': receiver.last_name, 
                    'email': receiver.email, 'phone': receiver.get_profile().phone}
    if receiver.get_profile().shipping_addresses.all().count() > 0:
      form.fields['shipping_addresses'] = forms.ChoiceField()
      form.fields['shipping_addresses'].widget.queryset = receiver.get_profile().shipping_addresses.all()

      current_shipping = receiver.get_profile().shipping_address

      initial_data['address1'] = current_shipping.street1
      initial_data['address2'] = current_shipping.street2
      initial_data['company_co'] = current_shipping.company_co
      initial_data['city'] = current_shipping.city
      initial_data['state'] = current_shipping.state
      initial_data['zipcode'] = current_shipping.zipcode
      initial_data['news_optin'] = receiver.get_profile().news_optin

  form.initial = initial_data
  data['form'] = form

  if 'ordering' in request.session and request.session['ordering']:
    # display different set of buttons if currently in address update stage
    data['update'] = True

  data["shop_menu"] = True
  return render_to_response("main/edit_shipping_address.html", data, context_instance=RequestContext(request))


@login_required
def edit_credit_card(request):
  """
    - Update or add credit card information

  """
  data = {}
  u = request.user

  form = PaymentForm(request.POST or None)
  #form = CreditCardForm(request.POST or None)

  if form.is_valid():
    new_card = form.save()
    try:
      receiver = User.objects.get(id=request.session['receiver_id'])
      profile = receiver.get_profile()
      profile.credit_card = new_card
      profile.save()
      # for now save the card to receiver 
      #if form.cleaned_data['save_card']:
      profile.credit_cards.add(new_card)
    except:
      # the receiver has not been specified
      raise PermissionDenied 

    # update cart status
    cart = Cart.objects.get(id=request.session['cart_id'])
    cart.status = Cart.CART_STATUS_CHOICES[4][0]
    cart.save()

    # go finalize order
    data["shop_menu"] = True
    return HttpResponseRedirect(reverse("place_order"))

  # display form: prepopulate with previous credit card used
  current_user_profile = u.get_profile()
  if 'ordering' in request.session and request.session['ordering'] and current_user_profile.credit_card:
    card_info = current_user_profile.credit_card
    form.initial = {'card_number': card_info.decrypt_card_num(), 'exp_month': card_info.exp_month, 
                    'exp_year': card_info.exp_year, 'verification_code': card_info.verification_code,
                    'billing_zipcode': card_info.billing_zipcode}
  else:
    cards = current_user_profile.credit_cards.all()
    if cards.count() > 0:
      card_info = cards[0]
      form.initial = {'card_number': card_info.decrypt_card_num(), 'exp_month': card_info.exp_month, 
                      'exp_year': card_info.exp_year, 'verification_code': card_info.verification_code,
                      'billing_zipcode': card_info.billing_zipcode}
  data['form'] = form
  if 'ordering' in request.session and request.session['ordering']:
    # display different set of buttons if currently in address update stage
    data['update'] = True

  data["shop_menu"] = True
  return render_to_response("main/edit_credit_card.html", data, context_instance=RequestContext(request))

