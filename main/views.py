# Create your views here.
from urlparse import urlparse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q

from main.models import Party, PartyInvite, MyHosts, Product, LineItem, Cart, CustomizeOrder, Order
from personality.models import Wine 

from main.forms import ContactRequestForm, PartyCreateForm, PartyInviteAttendeeForm, PartySpecialistSignupForm, AddWineToCartForm, AddTastingKitToCartForm, CustomizeOrderForm, ShippingForm, CreditCardForm, PaymentForm
from personality.forms import WineRatingsForm, AllWineRatingsForm
from accounts.models import VerificationQueue
from accounts.utils import send_verification_email, send_new_invitation_email, send_party_invitation_email, send_new_party_email
from main.utils import send_order_confirmation_email, send_host_vinely_party_email

from personality.utils import calculate_wine_personality

import json, uuid

from datetime import date, datetime, timedelta

@login_required
def home(request):
  data = {}

  u = request.user

  if request.user.is_authenticated():
    data["output"] = "User is authenticated"

    ps_group = Group.objects.get(name='Party Specialist')
    ph_group = Group.objects.get(name='Party Host')
    sp_group = Group.objects.get(name='Supplier')
    at_group = Group.objects.get(name='Attendee')

    if ps_group in u.groups.all():
      data["specialist"] = True
    if ph_group in u.groups.all():
      data["host"] = True
    if sp_group in u.groups.all():
      data["supplier"] = True
    if at_group in u.groups.all():
      data["attendee"] = True


    data['party_date'] = date.today() + timedelta(days=10)

    profile = u.get_profile()
    if profile.wine_personality:
      data['wine_personality'] = profile.wine_personality 
    else:
      data['wine_personality'] = False

    data['questionnaire_completed'] = profile.prequestionnaire 

    # go to home page

    # if user is party specialist
    # - be able to add new users and send them e-mail 
    # - see users registered at a party
    # - add a new host
    # - be able to order for a user
    # - be able to enter ratings for a user

    # if user is host
    # - list of parties (aggregate view of orders placed)
    # - list of attendees in each party (aggregate of what each attendee ordered)
    # - see orders placed by each attendee in detail 
    # - create party
    # - invite attendees

    # if user is attendee
    # - my wine personality
    # - order wine

    # if user is admin
  else:
    data["output"] = "User is not authenticated"
    return HttpResponseRedirect(reverse("landing_page"))

  return render_to_response("main/home.html", data, context_instance=RequestContext(request))

def about(request):
  """

  """

  data = {}

  return render_to_response("main/about.html", data, context_instance=RequestContext(request))

def contact_us(request):
  """

  """

  data = {}

  if request.method == "POST":
    form = ContactRequestForm(request.POST)
    if form.is_valid():
      form.save()
      return render_to_response("main/thankyou_contact.html", data, context_instance=RequestContext(request))
  else:
    form = ContactRequestForm()

  data["form"] = form

  return render_to_response("main/contact_us.html", data, context_instance=RequestContext(request))

@login_required
def host_vinely_party(request):
  """
    Host your own Vinely party
  """
  
  data = {}

  # sends a notification to the party specialist so this user can be upgraded to Host
  message = send_host_vinely_party_email(request)

  data["message"] = message

  return render_to_response("main/host_vinely_party.html", data, context_instance=RequestContext(request))

def how_it_works(request):
  """

  """

  data = {}

  return render_to_response("main/how_it_works.html", data, context_instance=RequestContext(request))

def start_order(request):
  """
    Show order page
  
    Add items to cart and go to cart view 
  """
  data = {}

  data["your_personality"] = "Moxie"
  products = Product.objects.filter(category=Product.PRODUCT_TYPE[1][0])

  data["products"] = products

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
  return render_to_response("main/order_tasting_kit.html", data, context_instance=RequestContext(request))


def cart_add_tasting_kit(request):
  """
    
    Add tasting kit to cart

    submit goes to checkout
  """
  data = {}

  u = request.user

  # TODO: check user personality and select the level

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

    return HttpResponseRedirect(reverse("cart"))

  product = Product.objects.get(category=Product.PRODUCT_TYPE[0][0])
  data["product"] = product
  form.initial = {'product': product, 'total_price': product.unit_price}
  data["form"] = form

  return render_to_response("main/cart_add_tasting_kit.html", data, context_instance=RequestContext(request))

def cart_add_wine(request, level="good"):
  """
    
    Add item to cart

    submit goes to checkout
  """
  data = {}

  u = request.user

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

    return HttpResponseRedirect(reverse("cart"))

  # big image of wine
  # TODO: need to check wine personality and choose the right product
  if level == "good":
    product = Product.objects.get(name="Good Level Name")
  elif level == "better":
    product = Product.objects.get(name="Better Level Name")
  elif level == "best":
    product = Product.objects.get(name="Best Level Name")
  elif level == "x":
    # not a valid product
    raise Http404

  data["product"] = product

  form.initial = {'level': level, 
                'total_price': product.unit_price,
                'product': product}
  data["form"] = form
  data["level"] = level

  return render_to_response("main/cart_add_wine.html", data, context_instance=RequestContext(request))

def cart(request):
  """
    
    Show items in cart, have a link to go back to start_order to order more

    submit goes to checkout
  """
  data = {}

  cart_id = request.session['cart_id']
  cart = Cart.objects.get(id=cart_id) 
  data["items"] = cart.items.all()
  data["cart"] = cart

  return render_to_response("main/cart.html", data, context_instance=RequestContext(request))

def cart_remove_item(request, cart_id, item_id):
  """
    Delete an item from cart
  """

  data = {}

  cart = Cart.objects.get(id=cart_id)
  item = LineItem.objects.get(id=item_id)
  
  cart.items.remove(item)

  return HttpResponseRedirect(request.GET.get("next"))

def customize_checkout(request):
  data = {}

  u = request.user

  if u.is_authenticated():
    try:
      custom = CustomizeOrder.objects.get(user=u) 
      # customization already happened

      # go to shipping 
      return HttpResponseRedirect(reverse('main.views.edit_shipping_address'))
    except CustomizeOrder.DoesNotExist:
      # continue to show customization form
      pass

  form = CustomizeOrderForm(request.POST or None)
  if form.is_valid():
    custom = form.save(commit=False)
    if u.is_authenticated():
      custom.user = u
    custom.save()
    return HttpResponseRedirect(reverse('main.views.edit_shipping_address'))
      
  form.initial = {'wine_mix': 0, 'sparkling': 0}
  data['form'] = form
  return render_to_response("main/customize_checkout.html", data, context_instance=RequestContext(request))

@login_required
def place_order(request):
  """
    This page allows you to review the order and finalize the order
 
    Credit card will also be charged
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

      # save cart to order
      return HttpResponseRedirect(reverse("order_complete", args=[order_id]))

    else:
      # review what you have ordered
      data["items"] = cart.items.all()
      data["cart" ] = cart

      data["receiver"] = receiver
      data["credit_card"] = profile.credit_card 
      data["shipping_address"] = profile.shipping_address

      return render_to_response("main/place_order.html", data, context_instance=RequestContext(request))
  else:
    messages.error(request, 'Your session expired, please start ordering again.')
    return HttpResponseRedirect(reverse("start_order"))

@login_required
def order_complete(request, order_id):

  data = {}

  u = request.user

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

  if order.ordered_by == u or order.receiver == u:

    data["order"] = order

    cart = order.cart
    data["cart"] = cart
    data["items"] = cart.items.all()

    # need to send e-mail
    send_order_confirmation_email(request, order_id)

    return render_to_response("main/order_complete.html", data, context_instance=RequestContext(request))
  else:
    raise PermissionDenied

@login_required
def order_history(request):

  data = {}
  u = request.user

  data["orders"] = Order.objects.filter( Q( ordered_by=u ) | Q( receiver=u ) )

  return render_to_response("main/order_history.html", data, context_instance=RequestContext(request))

@login_required
def supplier_order_backlog(request):
  """
    Orders that the supplier needs to fulfill
  """

  data = {}
  u = request.user

  data["orders"] = Order.objects.all()

  return render_to_response("main/supplier_order_backlog.html", data, context_instance=RequestContext(request))

@login_required
def view_orders(request):
  data = {}
  return render_to_response("main/view_orders.html", data, context_instance=RequestContext(request))

@login_required
def record_wine_ratings(request):
  """
    Record wine ratings for a particular wine.
    Used by party specialists or attendees themselves.
  """

  data = {}

  u = request.user

  ps_group = Group.objects.get(name="Party Specialist")
  att_group = Group.objects.get(name="Attendee")

  if (ps_group in u.groups.all()) or (att_group in u.groups.all()):
    # one can record ratings only if party specialist or attendee

    if request.method == "POST":
      form = WineRatingsForm(request.POST)
      if form.is_valid():
        form.save()      

        if (ps_group in u.groups.all()):
          # ask if you want to fill out next customer's ratings or order wine
          data["role"] = "specialist"
          
        if (att_group in u.groups.all()):
          # ask if you want order wine
          data["role"] = "attendee"

        return render_to_response("main/ratings_saved.html", data, context_instance=RequestContext(request))
    else:
      # show forms
      form = WineRatingsForm()

    data["form"] = form

    return render_to_response("main/record_wine_ratings.html", data, context_instance=RequestContext(request))
  else:
    raise Http404 

@login_required
def record_all_wine_ratings(request, email=None):
  """
    Record wine ratings.
    Used by party specialists or attendees themselves.

  """

  #TODO: Need to track the party specialist that is adding the ratings so that this attendee is linked
  #     to the party specialist

  data = {}

  u = request.user

  ps_group = Group.objects.get(name="Party Specialist")
  ph_group = Group.objects.get(name="Party Host")
  att_group = Group.objects.get(name="Attendee")

  if (ps_group in u.groups.all()) or (att_group in u.groups.all()):
    # one can record ratings only if party specialist or attendee

    if request.method == "POST":
      form = AllWineRatingsForm(request.POST)
      if form.is_valid():
        results = form.save() 
        data["invitee"] = results[0]

        personality = calculate_wine_personality(*results)
        data["personality"] = personality
         
        if (ps_group in u.groups.all()) or (ps_group in u.groups.all()):
          # ask if you want to fill out next customer's ratings or order wine
          data["role"] = "specialist"
        elif (att_group in u.groups.all()):
          # ask if you want order wine
          data["role"] = "attendee"

        return render_to_response("main/ratings_saved.html", data, context_instance=RequestContext(request))

    else:
      # show forms

      initial_data = { 'wine1': Wine.objects.get(number=1, active=True).id,
                        'wine2': Wine.objects.get(number=2, active=True).id,
                        'wine3': Wine.objects.get(number=3, active=True).id,
                        'wine4': Wine.objects.get(number=4, active=True).id,
                        'wine5': Wine.objects.get(number=5, active=True).id,
                        'wine6': Wine.objects.get(number=6, active=True).id
                        }

      if email:
        attendee = User.objects.get(email=email)
        initial_data['email'] = attendee.email
        initial_data['first_name'] = attendee.first_name
        initial_data['last_name'] = attendee.last_name

      form = AllWineRatingsForm(initial=initial_data)

    data["form"] = form

    return render_to_response("main/record_all_wine_ratings.html", data, context_instance=RequestContext(request))

  else:
    # user needs to be a party specialist or attendee to fill this out
    # attendee is filling out their own data
    raise Http404 

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

  ps_group = Group.objects.get(name="Party Specialist")
  ph_group = Group.objects.get(name="Party Host")
  sp_group = Group.objects.get(name='Supplier')
  at_group = Group.objects.get(name='Attendee')

  if ps_group in u.groups.all():
    data["specialist"] = True
  if ph_group in u.groups.all():
    data["host"] = True
  if sp_group in u.groups.all():
    data["supplier"] = True
  if at_group in u.groups.all():
    data["attendee"] = True

  today = datetime.today()

  if (ps_group in u.groups.all()):
    # need to filter to parties that a particular user manages
    my_hosts = MyHosts.objects.filter(specialist=u).values_list('host', flat=True)
    data['parties'] = Party.objects.filter(host__in=my_hosts, event_date__gte=today)
    data['past_parties'] = Party.objects.filter(host__in=my_hosts, event_date__lt=today)
  elif (ph_group in u.groups.all()):
    data['parties'] = Party.objects.filter(host=u, event_date__gte=today)
    data['past_parties'] = Party.objects.filter(host=u, event_date__lt=today)
  else:
    raise PermissionDenied 

  return render_to_response("main/party_list.html", data, context_instance=RequestContext(request))

@login_required
def party_add(request):
  """
    Add a new party
  """
  data = {}

  u = request.user

  ps_group = Group.objects.get(name="Party Specialist")
  ph_group = Group.objects.get(name="Party Host")
  sp_group = Group.objects.get(name='Supplier')
  at_group = Group.objects.get(name='Attendee')

  if ps_group in u.groups.all():
    data["specialist"] = True
  if ph_group in u.groups.all():
    data["host"] = True
  if sp_group in u.groups.all():
    data["supplier"] = True
  if at_group in u.groups.all():
    data["attendee"] = True

  data["no_perms"] = False
  if ps_group not in u.groups.all():
    # if not a party specialist, one does not have permissions
    data["no_perms"] = True
    return render_to_response("main/party_add.html", data, context_instance=RequestContext(request))

  if request.method == "POST":
    form = PartyCreateForm(request.POST)
    if form.is_valid():

      new_party = form.save()
      new_host = new_party.host

      # map host to a specialist
      my_hosts, created = MyHosts.objects.get_or_create(specialist=u, host=new_host)

      if not new_host.is_active:
        # new host, so send password and invitation
        temp_password = User.objects.make_random_password()
        new_host.set_password(temp_password)
        new_host.save()

        verification_code = str(uuid.uuid4())
        vque = VerificationQueue(user=new_host, verification_code=verification_code)
        vque.save()

        # send an invitation e-mail if new user created 
        send_new_party_email(request, verification_code, temp_password, new_host.email)

      # go to party list page
      return HttpResponseRedirect(reverse("party_list"))
  else:
    initial_data = {'event_day': datetime.today().strftime("%m/%d/%Y")}
    form = PartyCreateForm(initial=initial_data)

  data["form"] = form

  return render_to_response("main/party_add.html", data, context_instance=RequestContext(request))

@login_required
def party_attendee_list(request, party_id):
  """
    Show attendees of a party
  """

  data = {}

  u = request.user

  party = None
  if int(party_id) != 0:
    party = get_object_or_404(Party, pk=party_id)

  ps_group = Group.objects.get(name="Party Specialist")
  ph_group = Group.objects.get(name="Party Host")
  sp_group = Group.objects.get(name='Supplier')
  at_group = Group.objects.get(name='Attendee')

  if ps_group in u.groups.all():
    data["specialist"] = True
  if ph_group in u.groups.all():
    data["host"] = True
  if sp_group in u.groups.all():
    data["supplier"] = True
  if at_group in u.groups.all():
    data["attendee"] = True

  if ps_group in u.groups.all() or ph_group in u.groups.all() or sp_group in u.groups.all(): 
    
    invitees = PartyInvite.objects.filter(party=party)

    data["party"] = party
    data["invitees"] = invitees

    return render_to_response("main/party_attendee_list.html", data, context_instance=RequestContext(request))
  else:
    raise PermissionDenied 

@login_required
def party_attendee_invite(request, party_id=0):
  """
    Invite a new attendee to a party 

      - only allow host or party specialist to add
      - need to track who added and make sure the attendee is linked to that specialist or host

  """
  data = {}

  u = request.user

  if Party.objects.all().count() == 0:
    data["no_parties"] = True
    return render_to_response("main/party_attendee_invite.html", data, context_instance=RequestContext(request))

  party = None
  if int(party_id) != 0:
    party = get_object_or_404(Party, pk=party_id)

  ps_group = Group.objects.get(name='Party Specialist')
  ph_group = Group.objects.get(name='Party Host')
  if ps_group in u.groups.all() or ph_group in u.groups.all(): 
    if request.method == "POST":
      form = PartyInviteAttendeeForm(request.POST)
      if form.is_valid():
        new_invite = form.save()

        new_invitee = new_invite.invitee

        if new_invitee.is_active is False:
          # new user created through party invitation
          temp_password = User.objects.make_random_password()
          new_invitee.set_password(temp_password)
          new_invitee.save()

          verification_code = str(uuid.uuid4())
          vque = VerificationQueue(user=new_invitee, verification_code=verification_code)
          vque.save()

          # send an invitation e-mail if new user created 
          send_new_invitation_email(request, verification_code, temp_password, new_invite, new_invitee.email)
        else:
          send_party_invitation_email(request, verification_code, new_invite, new_invitee.email)

        return HttpResponseRedirect(reverse("party_attendee_list", args=[new_invite.party.id]))
    else:
      # if request is GET
      if int(party_id) == 0:
        # unspecified party
        form = PartyInviteAttendeeForm()
      else:
        # specified party
        initial_data = {'party': party}
        form =  PartyInviteAttendeeForm(initial=initial_data)

    data["form"] = form
    data["party"] = party

    return render_to_response("main/party_attendee_invite.html", data, context_instance=RequestContext(request))
  else:
    raise PermissionDenied 

@login_required
def supplier_party_list(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
def party_order_list(request, party_id):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
def pending_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
def fulfilled_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
def all_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

def edit_shipping_address(request):
  """
    - Update or add shipping address

    pre condition: cart has been created

  """
  data = {}

  # prepopulate with shipping address

  u = request.user

  if u.is_anonymous():
    form = ShippingForm(request.POST or None)
  else:
    form = ShippingForm(request.POST or None, instance=u)

  if form.is_valid():
    receiver = form.save()

    # update the receiver user
    request.session['receiver_id'] = receiver.id

    if receiver.is_active is False: 
      # new receiving user created 
      role = Group.objects.get(name="Attendee")
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
      return HttpResponseRedirect(reverse("place_order"))
    else:
      return HttpResponseRedirect(reverse("edit_credit_card"))

  # populate with initial data if user is authenticated
  initial_data = {}
  if u.is_authenticated():
    initial_data = {'first_name': u.first_name, 'last_name': u.last_name, 'email': u.email, 'phone': u.get_profile().phone}
    if u.get_profile().shipping_addresses.all().count() > 0:
      form.fields['shipping_addresses'] = forms.ChoiceField()
      form.fields['shipping_addresses'].widget.queryset = u.get_profile().shipping_addresses.all()

      current_shipping = u.get_profile().shipping_address

      initial_data['address1'] = current_shipping.street1
      initial_data['address2'] = current_shipping.street2
      initial_data['company_co'] = current_shipping.company_co
      initial_data['city'] = current_shipping.city
      initial_data['state'] = current_shipping.state
      initial_data['zipcode'] = current_shipping.zipcode
      initial_data['news_optin'] = u.get_profile().news_optin

  form.initial = initial_data
  data['form'] = form

  if 'ordering' in request.session and request.session['ordering']:
    # display different set of buttons if currently in address update stage
    data['update'] = True

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
    return HttpResponseRedirect(reverse("place_order"))

  # prepopulate with previous credit card used
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

  return render_to_response("main/edit_credit_card.html", data, context_instance=RequestContext(request))

@login_required
def edit_subscription(request):
  """
    Update one's subscription's

    - Cancel
    - Change product
    - Change frequency
  """
  data = {}

  return render_to_response("main/edit_subscription.html", data, context_instance=RequestContext(request))


