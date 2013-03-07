# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template, Context
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django_tables2 import RequestConfig

from main.models import Party, PartyInvite, MyHost, Product, LineItem, Cart, SubscriptionInfo, \
                        CustomizeOrder, Order, OrganizedParty, EngagementInterest, InvitationSent, ThankYouNote
from personality.models import WineTaste, GeneralTaste, WinePersonality
from accounts.models import VerificationQueue, Zipcode

from main.forms import ContactRequestForm, PartyCreateForm, PartyInviteTasterForm, \
                        AddWineToCartForm, AddTastingKitToCartForm, CustomizeOrderForm, ShippingForm, \
                        CustomizeInvitationForm, OrderFulfillForm, CustomizeThankYouNoteForm, EventSignupForm, \
                        AttendeesTable, PartyTasterOptionsForm, OrderHistoryTable, PartyEditDateForm

from accounts.utils import send_verification_email, send_new_party_email, check_zipcode, \
                        send_not_in_area_party_email
from main.utils import send_order_confirmation_email, send_host_vinely_party_email, send_new_party_scheduled_email, \
                        distribute_party_invites_email, UTC, send_rsvp_thank_you_email, \
                        send_contact_request_email, send_order_shipped_email, if_supplier, if_pro, \
                        calculate_host_credit, calculate_pro_commission, distribute_party_thanks_note_email, \
                        resend_party_invite_email, get_default_invite_message, my_pro, \
                        preview_party_invites_email, get_default_signature, send_host_request_party_email, \
                        send_new_party_scheduled_by_host_email, send_new_party_scheduled_by_host_no_pro_email, \
                        send_new_party_host_confirm_email, preview_party_thanks_note_email, preview_host_confirm_email, \
                        party_setup_completed_email
from accounts.forms import VerifyEligibilityForm, PaymentForm, AgeValidityForm, MakeTasterForm

from cms.models import ContentTemplate
from support.models import Email

import json, uuid
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.paginator import Paginator
import urllib

import stripe

from stripecard.models import StripeCard

import logging

log = logging.getLogger(__name__)


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

    data['questionnaire_completed'] = WineTaste.objects.filter(user=u).exists() and GeneralTaste.objects.filter(user=u).exists()

    pro, pro_profile = my_pro(u)
    data['my_pro'] = pro

    # TODO: if there are orders pending
    data['pending_ratings'] = False
    profile = u.get_profile()

    if profile.wine_personality and profile.wine_personality.name != WinePersonality.MYSTERY:
      data['wine_personality'] = profile.wine_personality
    else:
      data['wine_personality'] = False
    # if user is admin
  else:
    data["output"] = "User is not authenticated"
    return HttpResponseRedirect(reverse("landing_page"))

  return render_to_response("main/home.html", data, context_instance=RequestContext(request))


def uncover_personality(request):
  data = {}

  data['uncover_personality_menu'] = True
  sections = ContentTemplate.objects.get(key='uncover_personality').sections.all()
  data['uncover_personality'] = sections.get(category=0).content
  data['heading'] = sections.get(category=4).content
  return render_to_response("main/uncover_personality.html", data, context_instance=RequestContext(request))


def our_story(request):
  """

  """

  data = {}

  data['our_story_menu'] = True
  sections = ContentTemplate.objects.get(key='our_story').sections.all()
  data['our_story'] = sections.get(category=0).content
  data['heading'] = sections.get(category=4).content
  return render_to_response("main/our_story.html", data, context_instance=RequestContext(request))


def get_started(request):
  """
    Get started
  """

  data = {}

  u = request.user
  data['get_started_menu'] = True
  sections = ContentTemplate.objects.get(key='get_started').sections.all()
  data['get_started_general'] = sections.get(category=0).content
  data['get_started_host'] = sections.get(category=2).content
  data['get_started_pro'] = sections.get(category=3).content
  data['heading'] = sections.get(category=4).content
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
  # check for pro
  pro = None
  pros = MyHost.objects.filter(host=request.user).order_by('-timestamp')
  if pros.exists():
    pro = pros[0].pro
  else:
    my_host, created = MyHost.objects.get_or_create(pro=None, host=request.user)

  # sends a notification to the Vinely Pro so this user can be upgraded to Vinely Host
  message_body = send_host_vinely_party_email(request, request.user, pro)

  data["message"] = message_body

  return render_to_response("main/host_vinely_party.html", data, context_instance=RequestContext(request))


def how_it_works(request):
  """

  """

  data = {}
  sections = ContentTemplate.objects.get(key='how_it_works').sections.all()
  data["how_it_works_menu"] = True
  data['how_it_works'] = sections.get(category=0).content
  data['heading'] = sections.get(category=4).content
  data['sub_heading'] = sections.get(category=5).content

  return render_to_response("main/how_it_works.html", data, context_instance=RequestContext(request))


@login_required
def start_order(request, receiver_id=None, party_id=None):
  """
    Show wine subscription order page

    :param receiver_id: the user id of the user who's order is being fulfilled
                      for example, when a Vinely Pro enters rating data and continues an order
                      for a guest, the guest user id is the receiver_id
  """
  data = {}
  #: receiver's wine personality, or current user's wine personality
  personality = None
  party = None
  receiver = None
  u = request.user

  if 'receiver_id' in request.session:
    del request.session['receiver_id']

  # both receiver and party_id must be present or none at all
  if receiver_id or party_id:
    # ordering for a particular user
    receiver = get_object_or_404(User, pk=receiver_id)
    request.session['receiver_id'] = receiver.id

    # if party_id:
    # ordering from a particular party
    party = get_object_or_404(Party, pk=party_id)
    request.session['party_id'] = party.id

  data["your_personality"] = WinePersonality.MYSTERY
  data["MYSTERY_PERSONALITY"] = WinePersonality.MYSTERY

  if receiver_id:
    # can only order for others if you are the pro
    if u.get_profile().is_pro():
      try:
        OrganizedParty.objects.get(party=party, pro=u)

        # if not the pro then must have been invited to the party
        if u != receiver:  # True for the pro
          invite = PartyInvite.objects.get(invitee=receiver, party=party)
      except (OrganizedParty.DoesNotExist, PartyInvite.DoesNotExist):
        messages.error(request, 'You can only order for tasters at your own parties')
        return HttpResponseRedirect(reverse('party_list'))

    personality = receiver.get_profile().wine_personality

    # check receivers age first
    if receiver.get_profile().is_under_age():
      messages.warning(request, 'Confirm that that the person you are ordering for is over 21.')

  elif u.is_authenticated():
    # ordering for oneself
    personality = u.get_profile().wine_personality

  if personality:
    data["your_personality"] = personality.name

    # filter only wine packages
    products = Product.objects.filter(category=Product.PRODUCT_TYPE[1][0]).order_by('unit_price')

    for p in products:
      description_template = Template(p.description)
      p.description = description_template.render(Context({'personality': personality.name}))
      p.img_file_name = "%s_%s_prodimg.png" % (personality.suffix, p.cart_tag)
    data["products"] = products
    data["product_levels"] = [Product.BASIC, Product.SUPERIOR, Product.DIVINE]

  data["shop_menu"] = True
  today = timezone.now()

  if party:
    can_order = (today - party.event_date <= timedelta(hours=24))
    if receiver_id and party_id and can_order == False:
      messages.error(request, "You can only order for a taster up to 24 hours after the party.")
      return HttpResponseRedirect(reverse('personality.views.personality_rating_info', args=[receiver.email, party.id]))

  # return render_to_response("main/start_order.html", data, context_instance=RequestContext(request))
  return HttpResponseRedirect(reverse('cart_add_wine'))


@login_required
def cart_add_tasting_kit(request, party_id=0):
  """

    Add tasting kit to cart

    submit goes to checkout
  """
  data = {}

  u = request.user

  party = None
  today = timezone.now()

  try:
    party = Party.objects.get(id=party_id, host__id=u.id, event_date__gt=today)
    if party_id:
      # ordering from a particular party
      request.session['party_id'] = int(party_id)
  except Party.DoesNotExist:
    raise Http404

  # check how many invites and recommend number of taste kits
  # invites = PartyInvite.objects.filter(party=party)
  # if invites.count() == 0:
  #   messages.warning(request, 'No one has RSVP\'d for your party yet. It\'s good to know how many people will be coming so that you can know how many kits to order.')
  # elif invites.count() < 8:
  #   messages.info(request, 'We would recommended that you order 1 taste kit. This should be enough for your %s party tasters.' % invites.count())
  # elif invites.count() > 12 and invites.count() <= 24:
  #   messages.info(request, 'We would recommended that you order 2 taste kits since you have more than 6 tasters.')
  # elif invites.count() > 24:
  #   messages.warning(request, 'You can only order up to 2 taste kits at a time for up to 24 guests. Don\'t worry though, just finish this order and then make a new one.')
  # else:

  request.session['taste_kit_order'] = True

  form = AddTastingKitToCartForm(request.POST or None)

  if form.is_valid():
    # if ordering tasting kit make sure thats the only thing in the cart
    if 'cart_id' in request.session:
      cart = Cart.objects.get(id=request.session['cart_id'])
      if cart.items.exclude(product__category=Product.PRODUCT_TYPE[0][0]).exists():
        cart_url = reverse("cart")
        alert_msg = 'You can\'t order anything else when ordering a taste kit. Either clear your <a href="%s">cart</a> or checkout the existing <a href="%s">cart</a> first.' % (cart_url, cart_url)
        messages.error(request, mark_safe(alert_msg))
        return HttpResponseRedirect('.')

      if cart.party and cart.party != party:
        # if cart.party is None, no party has been assigned in previous orders
        messages.error(request, 'Looks like you\'ve already started ordering a taste kit for another party. You can only order taste kits for one party at a time.')
        return HttpResponseRedirect('.')

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

  if Product.objects.filter(category=Product.PRODUCT_TYPE[0][0], active=True).exists():
    products = Product.objects.filter(category=Product.PRODUCT_TYPE[0][0], active=True).order_by('unit_price')
    data["product"] = products[0]
    form.initial = {'product': products[0], 'total_price': products[0].unit_price, 'quantity': 1}
    data["form"] = form

  data["shop_menu"] = True
  messages.info(request, 'One taste kit can accomodate up to 12 people. If you plan on having more than 12 guests, order two kits.')
  return render_to_response("main/cart_add_tasting_kit.html", data, context_instance=RequestContext(request))


@login_required
def cart_add_wine(request):
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
  if 'receiver_id' in request.session:
    receiver = User.objects.get(id=request.session['receiver_id'])
  else:
    receiver = u
  data['receiver'] = receiver
  personality = receiver.get_profile().wine_personality
  # print personality
  form = AddWineToCartForm(request.POST or None)
  # print 'form.errors', form.errors
  if form.is_valid():
    # raise Exception
    # if ordering tasting kit make sure thats the only thing in the cart
    if 'cart_id' in request.session:
      cart = Cart.objects.get(id=request.session['cart_id'])
      if cart.items.filter(product__category=Product.PRODUCT_TYPE[0][0]).exists():
        alert_msg = 'A tasting kit is already in your cart.  Either clear it from your <a href="%s">cart</a> or checkout that order first.' % reverse("cart")
        messages.error(request, alert_msg)
        return HttpResponseRedirect('.')

    # hold on adding line item to cart until after verification theres no multiple subscription
    item = form.save(commit=False)

    if 'cart_id' in request.session:
      cart = Cart.objects.get(id=request.session['cart_id'])
      # cart.items.add(item)
      # cart.save()
    else:
      # create new cart
      if u.is_authenticated():
        cart = Cart(user=receiver)
      else:
        # anonymous cart
        cart = Cart()
      cart.save()
      request.session['cart_id'] = cart.id

    # can only order make one subscription at a time
    if (item.frequency == 1) and cart:
      if cart.items.filter(frequency=1).exists():
        alert_msg = 'You already have a subscription in your cart. Multiple subscriptions are not supported at this time. You can change this to a one-time purchase.'
        messages.error(request, alert_msg)
        return HttpResponseRedirect('.')

    # save item and add to cart after verifying no other item in cart
    item.total_price = item.subtotal()
    item.save()
    cart.items.add(item)

    # udpate cart status
    if party:
      cart.party = party
    cart.status = Cart.CART_STATUS_CHOICES[2][0]
    cart.adds += 1
    cart.discount = cart.calculate_discount()
    cart.save()
    # raise Exception
    # update customization options
    # custom, created = CustomizeOrder.objects.get_or_create(user=receiver)

    # if int(form.cleaned_data['mix_selection']) == 0:
    #   custom.wine_mix = int(form.cleaned_data['mix_selection'])
    # else:
    #   custom.wine_mix = int(form.cleaned_data['wine_mix'])
    # custom.save()

    # if not pro notify user if they are already subscribed and that a new subscription will cancel the existing
    pro_group = Group.objects.get(name="Vinely Pro")
    if pro_group not in u.groups.all():
      if cart.items.filter(frequency__in=[1, 2, 3]).exists():
        if SubscriptionInfo.objects.filter(user=u, frequency__in=[1, 2, 3]).exists():
          messages.warning(request, "You already have an existing subscription in the system. If you proceed, this action will cancel that subscription.")

    data["shop_menu"] = True
    return HttpResponseRedirect(reverse("cart"))

  # big image of wine
  # TODO: need to check wine personality and choose the right product
  # try:
  #   product = Product.objects.filter(active=True)[0]
  # except:
  #   # not a valid product
  #   raise Http404

  # description_template = Template(product.description)
  # product.description = description_template.render(Context({'personality': personality.name}))
  # product.img_file_name = "%s_%s_prodimg.png" % (personality.suffix, product.cart_tag)
  # # product.unit_price = product.full_case_price
  product = Product.objects.get(cart_tag="6")
  data["product"] = product
  data["personality"] = personality
  data["has_personality"] = receiver.get_profile().has_personality()
  form.initial = {'total_price': product.unit_price, 'product': product}
  data["form"] = form
  # data["level"] = level

  data["shop_menu"] = True
  return render_to_response("main/cart_add_wine.html", data, context_instance=RequestContext(request))


@login_required
def cart(request):
  """

    Show items in cart, have a link to go back to start_order to order more

    submit goes to checkout
  """
  u = request.user

  data = {}

  try:
    cart_id = request.session['cart_id']
    cart = Cart.objects.get(id=cart_id)
    cart.views += 1
    cart.save()

    if 'receiver_id' in request.session:
      personality = User.objects.get(id=request.session['receiver_id']).get_profile().wine_personality
    else:
      personality = u.get_profile().wine_personality

    if 'receiver_id' in request.session:
      data['receiver'] = User.objects.get(id=request.session['receiver_id'])

    data['items'] = []
    for item in cart.items.all():
      if item.product.category == 1:
        item.img_file_name = "%s_%s_prodimg.png" % (personality.suffix, item.product.cart_tag)
        # print item.img_file_name
      data['items'].append(item)

    data["cart"] = cart
    data['allow_customize'] = True
    # skip customizing if only ordering tasting kit
    check_cart = cart.items.filter(product__category=Product.PRODUCT_TYPE[0][0])
    if check_cart.exists():
      data['allow_customize'] = False
  except KeyError:
    # cart is empty
    data["items"] = []

  data["shop_menu"] = True

  return render_to_response("main/cart.html", data, context_instance=RequestContext(request))


@login_required
def cart_remove_item(request, cart_id, item_id):
  """
    Delete an item from cart
  """

  data = {}

  cart = Cart.objects.get(id=cart_id)
  item = LineItem.objects.get(id=item_id)
  if item.product.category == 0 and 'taste_kit_order' in request.session:
    del request.session['taste_kit_order']
  cart.items.remove(item)

  # track cart activity
  cart.removes += 1
  cart.save()

  data["shop_menu"] = True

  return HttpResponseRedirect(request.GET.get("next"))


@login_required
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

  if 'cart_id' not in request.session:
    messages.error(request, 'Your cart is empty. Please add something to the cart first.')
    return HttpResponseRedirect(reverse("cart"))

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
    cart = get_object_or_404(Cart, id=request.session['cart_id'])

    # receiver = get_object_or_404(User, id=request.session['receiver_id'])
    receiver = cart.receiver
    profile = receiver.get_profile()

    current_shipping = profile.shipping_address
    receiver_state = Zipcode.objects.get(code=current_shipping.zipcode).state

    data["receiver_state"] = receiver_state
    try:
      data["customization"] = CustomizeOrder.objects.get(user=receiver)
    except CustomizeOrder.DoesNotExist:
      pass

    cart.discount = cart.calculate_discount()
    cart.save()

    data['taste_kit_order'] = request.session.get('taste_kit_order')

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
      if request.session['stripe_payment']:
        order.stripe_card = profile.stripe_card
      else:
        order.credit_card = profile.credit_card

      order.shipping_address = profile.shipping_address
      order.save()

      cart.status = Cart.CART_STATUS_CHOICES[5][0]
      cart.save()

      if request.session.get('stripe_payment'):
        # charge card to stripe

        if receiver_state in Cart.STRIPE_STATES:
          if receiver_state == "CA":
            stripe.api_key = settings.STRIPE_SECRET_CA

        if cart.discount > 0:
          customer = stripe.Customer.retrieve(id=profile.stripe_card.stripe_user)
          coupon = stripe.Coupon.create(amount_off=int(cart.discount * 100), duration='once', currency='usd')
          customer.coupon = coupon.id
          customer.save()

        # NOTE: Amount must be in cents
        # Having these first so that they come last in the stripe invoice.
        stripe.InvoiceItem.create(customer=profile.stripe_card.stripe_user, amount=int(order.cart.shipping() * 100), currency='usd', description='Shipping')
        stripe.InvoiceItem.create(customer=profile.stripe_card.stripe_user, amount=int(order.cart.tax() * 100), currency='usd', description='Tax')
        non_sub_orders = order.cart.items.filter(frequency=0)
        sub_orders = order.cart.items.filter(frequency__in=[1, 2, 3])
        for item in non_sub_orders:
          stripe.InvoiceItem.create(customer=profile.stripe_card.stripe_user, amount=int(item.subtotal() * 100), currency='usd', description=LineItem.PRICE_TYPE[item.price_category][1])

        # create invoice manually if there's no subscription
        if non_sub_orders.exists() and not sub_orders.exists():
          invoice = stripe.Invoice.create(customer=profile.stripe_card.stripe_user)
          invoice.pay()

        # if subscription exists then create plan
        if sub_orders.exists():
          item = sub_orders[0]
          customer = stripe.Customer.retrieve(id=profile.stripe_card.stripe_user)
          stripe_plan = SubscriptionInfo.STRIPE_PLAN[item.frequency][item.price_category - 5]
          customer.update_subscription(plan=stripe_plan)

      # save cart to order
      data["shop_menu"] = True
      return HttpResponseRedirect(reverse("order_complete", args=[order_id]))

    else:
      # review what you have ordered
      if 'receiver_id' in request.session:
        personality = User.objects.get(id=request.session['receiver_id']).get_profile().wine_personality
      else:
        personality = u.get_profile().wine_personality

      data['items'] = []
      for item in cart.items.all():
        if item.product.category == 1:
          item.img_file_name = "%s_%s_prodimg.png" % (personality.suffix, item.product.cart_tag)
          # print item.img_file_name
        data['items'].append(item)

      data["cart"] = cart

      # record cart views
      cart.views += 1
      cart.save()

      data["receiver"] = receiver
      if request.session['stripe_payment']:
        data["credit_card"] = profile.stripe_card
      else:
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
  stripe_payment_mode = request.session.get('stripe_payment', None)

  # remove session information if it exists
  if 'ordering' in request.session:
    del request.session['ordering']
  if 'order_id' in request.session:
    del request.session['order_id']
  if 'cart_id' in request.session:
    del request.session['cart_id']
  if 'receiver_id' in request.session:
    del request.session['receiver_id']
  if 'stripe_payment' in request.session:
    del request.session['stripe_payment']

  try:
    order = Order.objects.get(order_id=order_id)
  except Order.DoesNotExist:
    raise Http404

  if order.fulfill_status == 0:
    # update subscription information if new order
    items = order.cart.items.filter(price_category__in=[12, 13, 14], frequency__in=[1])
    for item in items:
      # check if item contains subscription
      from_date = datetime.date(datetime.now(tz=UTC()))
      # create new subscription info
      subscription = SubscriptionInfo(user=order.receiver,
                                    quantity=item.price_category,
                                    frequency=item.frequency)

      if item.frequency == 1:
        next_invoice = from_date + relativedelta(months=+1)
      else:
        # set it to yesterday since subscription cancelled or was one time purchase
        # this way, celery task won't pick things up
        next_invoice = datetime.now(tz=UTC()) - timedelta(days=1)
      subscription.next_invoice_date = next_invoice
      subscription.updated_datetime = datetime.now(tz=UTC())
      subscription.save()

    if items.exists() and order.cart.party:
      # if subsciption order made at a party, then update receivers to be the party pro
      receiver_profile = order.receiver.get_profile()
      receiver_profile.mentor = order.cart.party.pro
      receiver_profile.save()

  if order.ordered_by == u or order.receiver == u:
    # only viewable by one who ordered or one who's receiving

    data["order"] = order

    cart = order.cart
    data["cart"] = cart

    personality = order.receiver.get_profile().wine_personality

    data['items'] = []
    for item in cart.items.all():
      if item.product.category == 1:
        item.img_file_name = "%s_%s_prodimg.png" % (personality.suffix, item.product.cart_tag)
        # print item.img_file_name
      data['items'].append(item)

    # need to send e-mail
    send_order_confirmation_email(request, order_id)

    stripe_card_used = order.stripe_card
    data["credit_card"] = stripe_card_used if stripe_payment_mode or stripe_card_used else order.credit_card
    data["shop_menu"] = True
    return render_to_response("main/order_complete.html", data, context_instance=RequestContext(request))
  else:
    raise PermissionDenied


@login_required
def order_history(request):

  data = {}
  u = request.user

  # data["orders"] = Order.objects.filter(Q(ordered_by=u) | Q(receiver=u))
  orders = Order.objects.filter(Q(ordered_by=u) | Q(receiver=u))

  table = OrderHistoryTable(orders, user=u)
  RequestConfig(request).configure(table)
  data['table'] = table

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

  today = timezone.now()

  my_pro_parties = OrganizedParty.objects.filter(pro=u).values_list('party', flat=True).distinct()
  if u.userprofile.is_pro():
    # need to filter to parties that a particular user manages
    # consider a party 'past' 24hours after event date
    party_valid_date = today - timedelta(hours=24)
    # parties managed
    data['pro_parties'] = Party.objects.filter(organizedparty__pro=u, event_date__gte=party_valid_date).order_by('event_date')
    data['pro_past_parties'] = Party.objects.filter(organizedparty__pro=u, event_date__lt=party_valid_date).order_by('-event_date')

    # parties hosted
    data['host_parties'] = Party.objects.filter(host=u, event_date__gte=today).exclude(id__in=my_pro_parties).order_by('event_date')
    data['host_past_parties'] = Party.objects.filter(host=u, event_date__lt=today).exclude(id__in=my_pro_parties).order_by('-event_date')

    pro_comm, mentee_comm = calculate_pro_commission(u)
    data['pro_commission'] = pro_comm
    data['mentee_commission'] = mentee_comm
    data['total_commission'] = pro_comm + mentee_comm
  elif u.userprofile.is_host():
    data['host_credits'] = calculate_host_credit(u)
    data['host_parties'] = Party.objects.filter(host=u, event_date__gte=today).order_by('event_date')
    data['host_past_parties'] = Party.objects.filter(host=u, event_date__lt=today).order_by('-event_date')

  # parties attended
  # exclude parties in which user was the host or pro
  data['taster_parties'] = Party.objects.filter(partyinvite__invitee=u, event_date__gte=today).exclude(host=u).exclude(id__in=my_pro_parties).order_by('event_date')
  data['taster_past_parties'] = Party.objects.filter(partyinvite__invitee=u, event_date__lt=today).exclude(host=u).exclude(id__in=my_pro_parties).order_by('-event_date')
  pro, pro_profile = my_pro(u)
  data['my_pro'] = pro
  data["parties_menu"] = True

  return render_to_response("main/party_list.html", data, context_instance=RequestContext(request))


@login_required
def party_host_list(request, host_name_email):
  pro = request.user
  host_name_email = host_name_email.strip()

  # show people who RSVP'ed to the party
  my_hosts = MyHost.objects.filter(pro=pro)
  users = User.objects.filter(id__in=[x.host.id for x in my_hosts])
  users = users.filter(Q(first_name__icontains=host_name_email) | Q(last_name__icontains=host_name_email) | Q(email__icontains=host_name_email)).order_by('first_name')
  data = ['%s %s, %s' % (x.first_name, x.last_name, x.email) for x in users]

  return HttpResponse(json.dumps(data), mimetype="application/json")


@login_required
def my_taster_list(request, taster_name_email):
  u = request.user
  taster_name_email = taster_name_email.strip()

  if u.userprofile.is_host():
    # only get users linked to this host
    my_guests = PartyInvite.objects.filter(party__host=u)
    users = User.objects.filter(Q(first_name__icontains=taster_name_email) | Q(last_name__icontains=taster_name_email) | Q(email__icontains=taster_name_email), id__in=[x.invitee.id for x in my_guests]).order_by('first_name')
  elif u.userprofile.is_pro():
    # only get users linked to this pro
    my_guests = PartyInvite.objects.filter(party__organizedparty__pro=u)
    users = User.objects.filter(Q(first_name__icontains=taster_name_email) | Q(last_name__icontains=taster_name_email) | Q(email__icontains=taster_name_email), id__in=[x.invitee.id for x in my_guests]).order_by('first_name')
  else:
    # nothing
    users = User.objects.none()

  data = ['%s %s, %s' % (x.first_name, x.last_name, x.email) for x in users]

  return HttpResponse(json.dumps(data), mimetype="application/json")


@login_required
def party_user_info(request, user_email):
  data = {}
  user = User.objects.get(email=user_email)
  data['first_name'] = user.first_name
  data['last_name'] = user.last_name
  data['email'] = user.email
  data['phone'] = user.userprofile.phone

  # TODO: use most recent address used for this host

  return HttpResponse(json.dumps(data), mimetype="application/json")


@login_required
# @user_passes_test(if_pro, login_url="/pros/only/")
def party_add(request, party_id=None, party_pro=None):
  """
    Add a new party
  """
  data = {}

  u = request.user

  sp_group = Group.objects.get(name='Supplier')
  tas_group = Group.objects.get(name='Vinely Taster')

  pending_pro = Group.objects.get(name="Pending Vinely Pro")

  data["no_perms"] = False

  if sp_group in u.groups.all() or tas_group in u.groups.all() or pending_pro in u.groups.all():
    # if not a Vinely Pro or Host, one does not have permissions
    data["no_perms"] = True
    data["pending_pro"] = pending_pro in u.groups.all()
    return render_to_response("main/party_add.html", data, context_instance=RequestContext(request))

  initial_data = {}  # 'event_day': datetime.today().strftime("%m/%d/%Y")}

  if u.userprofile.is_host() and not party_id:
    return HttpResponseRedirect(reverse('pros_only'))

  party = None

  if party_id:
    if u.userprofile.is_host():
      party = get_object_or_404(Party, pk=party_id, host=u)
    else:
      party = get_object_or_404(Party, pk=party_id, organizedparty__pro=u)

    if party.event_date < timezone.now():
      messages.warning(request, "You cannot change party details for a past event.")
      return HttpResponseRedirect(reverse('party_details', args=[party_id]))

    # if party.confirmed and not (u.userprofile.events_manager() or party.host != u):
    #   messages.warning(request, "You cannot change party details once the party confirmation request has been sent out")
    #   return HttpResponseRedirect(reverse('party_details', args=[party_id]))

  self_hosting = True
  if u.userprofile.is_pro() and party_pro != 'pro' and not party_id:
    self_hosting = False

  data['self_hosting'] = self_hosting

  if u.userprofile.is_host() or self_hosting:
    initial_data['first_name'] = u.first_name
    initial_data['last_name'] = u.last_name
    initial_data['email'] = u.email
    initial_data['phone'] = u.get_profile().phone
    initial_data['host'] = u
    # pre-load address with most recent party's address
    parties = Party.objects.filter(host=u).order_by('-id')
    most_recent_party = parties[0] if parties.exists() else None

  else:
    # is pro
    initial_data['pro'] = u
    parties = Party.objects.filter(organizedparty__pro=u).order_by('-id')
    most_recent_party = parties[0] if parties.exists() else None

  if self_hosting:
    if most_recent_party and most_recent_party.address:
      # initial_data['address'] = most_recent_party.address
      initial_data['street1'] = most_recent_party.address.street1
      initial_data['street2'] = most_recent_party.address.street2
      initial_data['city'] = most_recent_party.address.city
      initial_data['state'] = most_recent_party.address.state
      initial_data['zipcode'] = most_recent_party.address.zipcode

  if party and party.address:
    initial_data['host'] = party.host
    # initial_data['address'] = party.address
    initial_data['street1'] = party.address.street1
    initial_data['street2'] = party.address.street2
    initial_data['city'] = party.address.city
    initial_data['state'] = party.address.state
    initial_data['zipcode'] = party.address.zipcode

    party_date = timezone.localtime(party.event_date)
    initial_data['event_day'] = party_date.strftime("%m/%d/%Y")
    initial_data['event_time'] = party_date.strftime("%I:%M %p")
    party.setup_stage = 1
    party.save()

  else:
    party_date = timezone.now() + timedelta(days=15)
    party_date = timezone.datetime(year=party_date.year, month=party_date.month, day=party_date.day,
                                    hour=19, minute=0)
    initial_data['event_day'] = party_date.strftime("%m/%d/%Y")
    initial_data['event_time'] = party_date.strftime("%I:%M %p")
  initial_data['self_hosting'] = self_hosting

  form = PartyCreateForm(request.POST or None, initial=initial_data, instance=party, user=u)

  if form.errors.get('__all__'):
    messages.error(request, form.errors['__all__'])

  if request.method == "POST":
    if form.is_valid():
      new_party = form.save(commit=False)

      if request.POST.get('preview'):
        preview = preview_host_confirm_email(request, new_party)
        data['preview'] = preview
        return render_to_response("main/party_host_confirmation_preview.html", data, context_instance=RequestContext(request))

      if u.userprofile.is_pro() and not u.userprofile.events_manager() and new_party.host != u:
        # new_party.confirmed = True
        new_party.requested = True
      if party:
        old_party = Party.objects.get(pk=party.id)
        new_party.auto_invite = old_party.auto_invite
        new_party.auto_thank_you = old_party.auto_thank_you
        new_party.guests_can_invite = old_party.guests_can_invite
        new_party.guests_see_guestlist = old_party.guests_see_guestlist
        new_party.confirmed = old_party.confirmed
        new_party.requested = old_party.requested
        # new_party.setup_stage = 1
      new_party.save()
      new_host = new_party.host

      # map host to a pro
      if u.userprofile.is_pro():
        applicable_pro = u
      else:
        applicable_pro, pro_profile = my_pro(u)

      no_applicable_pro = MyHost.objects.filter(host=new_host, pro__isnull=True)

      if no_applicable_pro.exists():
        if applicable_pro:
          my_hosts = no_applicable_pro[0]
          my_hosts.pro = applicable_pro
          my_hosts.save()
      else:
        my_hosts, created = MyHost.objects.get_or_create(pro=applicable_pro, host=new_host)

      # if there's an applicable pro create OrganizedParty now, will apply pro when one is assigned
      pro_parties, created = OrganizedParty.objects.get_or_create(pro=applicable_pro, party=new_party)
      if applicable_pro:
        # make the pro a mentor to the host
        host_profile = new_host.get_profile()
        # TODO: dont overwrite host's pro
        # host_profile.mentor = applicable_pro
        host_profile.save()

      if self_hosting:
        # Add host as invitee
        invited_host, created = PartyInvite.objects.get_or_create(invitee=new_host, party=new_party)
        if created:
          invited_host.response = 3
          invited_host.rsvp_code = str(uuid.uuid4())
          invited_host.save()

      if u.userprofile.is_pro() and not u.userprofile.events_manager():
        if not new_host.is_active:
          # new host, so send password and invitation
          temp_password = User.objects.make_random_password()
          new_host.set_password(temp_password)
          new_host.save()

          verification_code = str(uuid.uuid4())
          vque = VerificationQueue(user=new_host, verification_code=verification_code)
          vque.save()

          # send an invitation e-mail if new host created
          send_new_party_email(request, verification_code, temp_password, new_host.email)
          # send_new_party_scheduled_email(request, new_party)
        # else:
        #   # existing host needs to notified that party has been arranged
        #   if not u.userprofile.events_manager() and new_host != u:
        #     send_new_party_scheduled_email(request, new_party)
        #     messages.success(request, "Party (%s) has been successfully scheduled." % (new_party.title, ))

      # else:
      #   messages.success(request, "%s details have been successfully saved" % (new_party.title, ))

      data["parties_menu"] = True

      if request.POST.get('create'):
        # go to party details page
        send_new_party_host_confirm_email(request, new_party)
        # return HttpResponseRedirect(reverse("party_host_confirmation_preview", args=[new_party.id, email.id]))
        return HttpResponseRedirect(reverse("party_details", args=[new_party.id]))

      if request.POST.get('save'):
        messages.success(request, "%s details have been successfully saved" % (new_party.title, ))
        return HttpResponseRedirect(reverse("party_add", args=[new_party.id]))
      else:
        # messages.success(request, "%s details have been successfully saved" % (new_party.title, ))
        return HttpResponseRedirect(reverse('party_write_invitation', args=[new_party.id]))
  else:
    # GET
    # if the current user is host, display Vinely Pro
    if data.get("host"):
      pros = MyHost.objects.filter(host=u)
      if pros.exists():
        pro = pros[0].pro
        data["my_pro"] = pro
        send_host_vinely_party_email(request, u, pro)
      else:
        send_host_vinely_party_email(request, u)

  applicable_pro, pro_profile = my_pro(u)
  data["pro_user"] = applicable_pro
  data["form"] = form
  data["parties_menu"] = True

  return render_to_response("main/party_add.html", data, context_instance=RequestContext(request))


#@require_POST
@login_required
def party_edit_date(request, party_id):
  u = request.user

  data = {}
  party = get_object_or_404(Party, pk=party_id, organizedparty__pro=u)
  data['party'] = party

  initial_data = {}
  party_date = timezone.localtime(party.event_date)
  initial_data['event_day'] = party_date.strftime("%m/%d/%Y")
  initial_data['event_time'] = party_date.strftime("%I:%M %p")

  previous_page = request.GET.get('next', reverse('party_details', args=[party.id]))
  data['previous_page'] = previous_page

  edit_date_form = PartyEditDateForm(request.POST or None, initial=initial_data, instance=party)

  if edit_date_form.is_valid():
    event_date = edit_date_form.cleaned_data['event_date']
    log.info('Event Date: %s' % event_date)
    party.event_date = event_date
    party.save()
    return HttpResponseRedirect(previous_page)
  else:
    messages.warning(request, edit_date_form.errors['__all__'])

  data['edit_date_form'] = edit_date_form
  return HttpResponseRedirect(previous_page)


# @login_required
def party_add_taster(request, party, taster_form):
  u = request.user

  if taster_form.errors.get('__all__'):
    messages.error(request, taster_form.errors['__all__'])

  if taster_form.is_valid():
    new_invite = taster_form.save()
    new_invite.invited_by = u
    new_invite.rsvp_code = str(uuid.uuid4())
    new_invite.save()
    invitee = new_invite.invitee

    messages.success(request, '%s %s (%s) has been added to the party invitations list.' % (invitee.first_name, invitee.last_name, invitee.email))


@login_required
def party_find_friends(request, party_id):
  data = {}
  u = request.user

  if u.userprofile.events_manager():
    party = get_object_or_404(Party, id=party_id)
  else:
    party = get_object_or_404(Party, id=party_id, host=u)

  party.setup_stage = 3
  party.save()

  if party.requested and not (u.userprofile.events_manager() or u.userprofile.is_pro):
    messages.warning(request, "You cannot change party details once the party request has been sent to the Pro")
    return HttpResponseRedirect(reverse('party_details', args=[party_id]))

  data["parties_menu"] = True
  data['invitees'] = PartyInvite.objects.filter(party=party).exclude(invitee=party.host).order_by('invitee__first_name', 'invitee__last_name')

  initial_data = {'party': party}

  if request.POST.get('add_taster'):
    taster_form = PartyInviteTasterForm(request.POST, initial=initial_data)
    party_add_taster(request, party, taster_form)
  else:
    taster_form = PartyInviteTasterForm(initial=initial_data)

  if request.POST.get("next"):
    return HttpResponseRedirect(reverse('party_review_request', args=[party.id]))

  # if request.POST.get('add_vinely_party'):
  #   # added as vinely event - only possible by pro
  #   party.requested = True
  #   party.confirmed = True
  #   # party.setup_stage = 3
  #   party.save()

  #   return HttpResponseRedirect(reverse('party_details', args=[party.id]))

  data['party'] = party
  data['taster_form'] = taster_form
  return render_to_response("main/party_find_friends.html", data, context_instance=RequestContext(request))


@login_required
def party_review_request(request, party_id):
  data = {}
  u = request.user

  # need to show all the party information

  if u.userprofile.events_manager():
    party = get_object_or_404(Party, id=party_id)
  else:
    party = get_object_or_404(Party, id=party_id, host=u)

  party.setup_stage = 4
  party.save()

  initial_data = {'party': party}

  allowed_taster_actions = []

  if party.guests_can_invite:
    allowed_taster_actions.append(PartyTasterOptionsForm.TASTER_OPTIONS[1][0])

  if party.guests_see_guestlist:
    allowed_taster_actions.append(PartyTasterOptionsForm.TASTER_OPTIONS[0][0])

  initial_data['taster_actions'] = allowed_taster_actions
  initial_data['auto_thank_you'] = 1 if party.auto_thank_you else 0

  options_form = PartyTasterOptionsForm(request.POST or None, initial=initial_data)

  if options_form.is_valid():
    # once party is confirmed these fields are no longer visible for edit
    if not party.confirmed:
      party.auto_invite = options_form.cleaned_data['auto_invite']
      party.auto_thank_you = options_form.cleaned_data['auto_thank_you']

    guest_options = [int(x) for x in options_form.cleaned_data['taster_actions']]
    party.guests_see_guestlist = True if 0 in guest_options else False
    party.guests_can_invite = True if 1 in guest_options else False
    party.save()

    if request.POST.get('preview'):
      return HttpResponseRedirect(reverse('party_preview_invitation', args=[party.id]))

  if request.POST.get('request_party'):

    # party request made
    party.created = timezone.now()
    party.requested = True
    party.confirmed = True
    party.save()
    # Send confirmation request to Pro
    # send_host_request_party_email(request, party)
    # party_has_pro = OrganizedParty.objects.filter(party=party)
    # if party_has_pro.exists():
    #   send_new_party_scheduled_by_host_email(request, party)
    #   # messages.success(request, "You have scheduled your party but it still needs to be confirmed by your Pro before your invite can be sent out.")
    # else:
    #   send_new_party_scheduled_by_host_no_pro_email(request, party)
    # send notification to pro
    party_setup_completed_email(request, party)

    invitation = InvitationSent.objects.filter(party=party).order_by('-id')[0]
    invites = PartyInvite.objects.filter(party=party).exclude(invitee=party.host)
    for invite in invites:
      invitation.guests.add(invite.invitee)
    # send e-mails
    distribute_party_invites_email(request, invitation)

      # messages.success(request, "You have submitted your party but you still need to be paired with a Vinely Pro and have the party confirmed before your invite can be sent out.")
    messages.success(request, "Your invitations were sent successfully to your tasters.")
    return HttpResponseRedirect(reverse("party_details", args=[party.id]))

  if request.POST.get('add_party'):
    # only possible by pro
    party.requested = True
    party.confirmed = True
    party.save()

    invitation = InvitationSent.objects.filter(party=party).order_by('-id')[0]
    invites = PartyInvite.objects.filter(party=party).exclude(invitee=party.host)
    for invite in invites:
      invitation.guests.add(invite.invitee)
    # send e-mails
    distribute_party_invites_email(request, invitation)

    messages.success(request, "Party (%s) has been successfully scheduled." % (party.title, ))
    return HttpResponseRedirect(reverse("party_details", args=[party.id]))

  data['party'] = party
  data['invitees'] = PartyInvite.objects.filter(party=party).exclude(invitee=party.host).order_by('invitee__first_name', 'invitee__last_name')

  applicable_pro, pro_profile = my_pro(u)
  data["pro_user"] = applicable_pro

  try:
    invitation = InvitationSent.objects.filter(party=party).order_by('-id')[0]
  except:
    raise Http404

  preview = preview_party_invites_email(request, invitation, embed=True)
  data["parties_menu"] = True
  data["invite_preview"] = preview
  data['options_form'] = options_form
  return render_to_response("main/party_review_request.html", data, context_instance=RequestContext(request))


@login_required
def party_cancel(request, party_id):

  u = request.user

  # TODO: display warning that all party information will be destroyed
  if u.userprofile.events_manager():
    party = get_object_or_404(Party, id=party_id)
  else:
    party = get_object_or_404(Party, id=party_id, host=u)

  # TODO: remove partyinvites
  # for inv in PartyInvite.objects.filter(party=party):
  #   inv.delete()
  # TODO: remove OrganizedParty record
  # organizer = OrganizedParty.objects.get(party=party)
  # organizer.delete()
  # Does deleting party cascade delete all of above?
  party.delete()
  return HttpResponseRedirect(reverse('party_add'))


@login_required
def party_remove_taster(request, invite_id):

  invite = get_object_or_404(PartyInvite, pk=invite_id)
  success_url = request.GET.get('next', reverse('party_details', args=[invite.party.id]))
  # party = invite.party
  invite.delete()

  return HttpResponseRedirect(success_url)


@login_required
def party_edit_taster_info(request, invite_id, change_rsvp=None):
  data = {}
  u = request.user

  invite = get_object_or_404(PartyInvite, pk=invite_id)

  initial_data = {'host': u, "first_name": invite.invitee.first_name,
                  'last_name': invite.invitee.last_name, 'email': invite.invitee.email,
                  'phone': invite.invitee.get_profile().phone, 'change_rsvp': change_rsvp,
                  'rsvp_code': invite.rsvp_code}

  form = PartyInviteTasterForm(request.POST or None, initial=initial_data, instance=invite)

  previous_page = request.GET.get('next', reverse('party_details', args=[invite.party.id]))
  data['previous_page'] = previous_page

  if request.method == 'POST':
    if form.is_valid():
      old_invite = PartyInvite.objects.get(id=invite_id)
      invite = form.save()
      invite.invited_timestamp = old_invite.invited_timestamp
      invite.invited_by = old_invite.invited_by
      invite.rsvp_code = old_invite.rsvp_code if old_invite.rsvp_code else str(uuid.uuid4())
      invite.save()
      invitee = invite.invitee

      # you can only change names if it's a new user
      if not invitee.is_active:
        invitee.first_name = form.cleaned_data['first_name']
        invitee.last_name = form.cleaned_data['last_name']
        invitee.save()
        invitee_profile = invitee.get_profile()
        invitee_profile.phone = form.cleaned_data['phone']
        invitee_profile.save()
      messages.success(request, 'Details for %s %s (%s) have been updated.' % (invitee.first_name, invitee.last_name, invitee.email))
    else:
      messages.error(request, form.errors)
    return HttpResponseRedirect(previous_page)

  data['change_rsvp'] = change_rsvp
  data['party'] = invite.party
  data['taster_form'] = form
  data['invite'] = invite
  return render_to_response("main/party_edit_taster_modal.html", data, context_instance=RequestContext(request))


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

  initial_data = {'party': party}

  taster_form = PartyInviteTasterForm(request.POST or None, initial=initial_data)
  data['invite_form'] = CustomizeInvitationForm(initial={'subject': 'hide'})

  data['taster_form'] = taster_form
  party_add_taster(request, party, taster_form)

  invitees = PartyInvite.objects.filter(party=party)

  data["party"] = party
  data["invitees"] = invitees

  # these checks are only relevant to host or Pro for upcoming parties
  kit_order_date = party.event_date - timedelta(days=10)
  can_order_kit = (party.event_date - timezone.now() >= timedelta(days=10))

  # initialize the edit party info form
  edit_form_data = {}
  party_date = timezone.localtime(party.event_date)
  edit_form_data['event_day'] = party_date.strftime("%m/%d/%Y")
  edit_form_data['event_time'] = party_date.strftime("%I:%M %p")

  edit_date_form = PartyEditDateForm(request.POST or None, initial=edit_form_data, instance=party)
  data['edit_date_form'] = edit_date_form

  # these checks are only relevant to host or Pro
  if can_order_kit and (party.pro == u or party.host == u):
    if party.host != u and not u.userprofile.events_manager():
      # if not u.userprofile.events_manager():
      if party.confirmed:
        if not party.kit_ordered():
          msg = 'Your host needs to order their tasting kit by %s' % kit_order_date.strftime("%m/%d/%Y")
          messages.warning(request, msg)
      else:
        pro_name = party.host.first_name if party.host.first_name else 'Anonymous'
        pro_name = pro_name + "'" if pro_name.endswith('s') else pro_name + "'s"
        # msg = '%s party date and time need confirmation for %s  <a href="%s" class="btn btn-primary">  Confirm</a>' % (pro_name, party.event_date.strftime("%B %d, at %I:%M %p"), reverse('party_confirm', args=[party.id]))
        # messages.warning(request, msg)
    else:
      # for host
      if party.confirmed and not u.userprofile.events_manager():
        if party.invite_sent():
          if not party.kit_ordered():
            msg = 'You need to order your tasting kit by %s.  <a href="%s" class="btn btn-primary">Order tasting kit</a>' % (kit_order_date.strftime("%m/%d/%Y"), reverse('cart_add_tasting_kit', args=[party.id]))
            messages.warning(request, msg)
          # TODO: if kit ordered but number is still higher than kit
          # ask to order another kit
        else:
          msg = 'Your party date and time have been confirmed! Let\'s get this party started and send out your invite!'
          messages.warning(request, msg)
      # else:
      #   msg = 'Congratulations! Your invite is almost ready to go out. We\'re just waiting for you to complete the invitation process.'
      #   messages.info(request, msg)

  data["pro_user"] = party.pro
  data["parties_menu"] = True
  data["MYSTERY_PERSONALITY"] = WinePersonality.MYSTERY
  data['can_order_kit'] = can_order_kit

  # pro can only shop for taster upto 24hrs after party
  today = timezone.now() - timedelta(days=1)
  data['can_shop_for_taster'] = ((party.event_date > today) and (party.event_date - timezone.now() <= timedelta(days=1)))
  data['can_add_taster'] = (party.event_date > today)
  data['completed'] = "Yes" if WineTaste.objects.filter(user=u).exists() and GeneralTaste.objects.filter(user=u).exists() else "No"

  table = AttendeesTable(invitees, user=u, data=data)
  RequestConfig(request).configure(table)
  data['table'] = table

  data['invitees_table'] = invitees
  # if data['can_shop_for_taster']:
  return render_to_response("main/party_details.html", data, context_instance=RequestContext(request))
  # else:
  #   orders = Order.objects.filter(cart__party=party)
  #   data['buyers'] = invitees.filter(invitee__in=[x.receiver for x in orders])
  #   data['non_buyers'] = invitees.exclude(invitee__in=[x.receiver for x in orders])
  #   return render_to_response("main/party_host_thanks.html", data, context_instance=RequestContext(request))


@login_required
def party_confirm(request, party_id):
  u = request.user
  party = get_object_or_404(Party, pk=party_id)
  party.confirmed = True
  party.save()

  org_party = OrganizedParty.objects.get(party=party)
  org_party.pro = u
  org_party.save()

  if party.auto_invite:
    invitation = InvitationSent.objects.filter(party=party).order_by('-id')[0]
    # send e-mails
    distribute_party_invites_email(request, invitation)

  messages.success(request, 'Congratulations! Your party has been scheduled')
  return HttpResponseRedirect(reverse('party_details', args=[party.id]))


# @login_required
# def party_taster_list(request, party_id):
#   """
#     Show Vinely Tasters of a party
#   """

#   data = {}

#   u = request.user

#   party = None
#   if party_id and int(party_id) != 0:
#     party = get_object_or_404(Party, pk=party_id)

#   invitees = PartyInvite.objects.filter(party=party)

#   data["party"] = party
#   data["invitees"] = invitees
#   data["parties_menu"] = True

#   return render_to_response("main/party_taster_list.html", data, context_instance=RequestContext(request))


# @login_required
def party_taster_invite(request, rsvp_code=None, party_id=0):
  """
    Invite a new Vinely Taster to a party

      - only allow host or Vinely Pro to add
      - need to track who added and make sure the Vinely Taster is linked to that pro or host

  """
  data = {}

  u = request.user

  if Party.objects.all().count() == 0:
    data["no_parties"] = True
    return render_to_response("main/party_taster_invite.html", data, context_instance=RequestContext(request))

  pro_group = Group.objects.get(name='Vinely Pro')
  hos_group = Group.objects.get(name='Vinely Host')
  tas_group = Group.objects.get(name='Vinely Taster')

  if not rsvp_code and not u.is_authenticated():
    return HttpResponseRedirect(reverse('login') + '?next=' + request.path)

  party = None
  if int(party_id) != 0:
    party = get_object_or_404(Party, pk=party_id)

    if tas_group in u.groups.all():
      try:
        # Vinely Taster must have been already invited to invite more
        invite = PartyInvite.objects.get(party=party, invitee=u)
      except PartyInvite.DoesNotExist:
        raise PermissionDenied

  if u.is_authenticated():
    invite = get_object_or_404(PartyInvite, party=party, invitee=u)
  else:
    invite = get_object_or_404(PartyInvite, party=party, rsvp_code=rsvp_code)
    u = invite.invitee

  if pro_group in u.groups.all() or hos_group in u.groups.all() or tas_group in u.groups.all():
    if u.get_profile().is_host():
      initial_data = {'host': u}
    elif u.get_profile().is_pro():
      initial_data = {'pro': u}
    else:
      initial_data = {}

    if request.method == "POST":
      form = PartyInviteTasterForm(request.POST, initial=initial_data)
      if form.is_valid():
        new_invite = form.save()
        new_invite.invited_by = u
        new_invite.rsvp_code = str(uuid.uuid4())
        new_invite.save()

        new_invitee = new_invite.invitee
        # removed following lines since invitation get sent in a batch from the UI
        #else:
        #  send_party_invitation_email(request, new_invite)

        messages.success(request, '%s %s (%s) has been added to the party invitations list.' % (new_invitee.first_name, new_invitee.last_name, new_invitee.email))

        data["parties_menu"] = True
        return HttpResponseRedirect(reverse("party_details", args=[new_invite.party.id]))
    else:
      # if request is GET
      if int(party_id) == 0:
        # unspecified party
        form = PartyInviteTasterForm(initial=initial_data)
      else:
        # specified party
        initial_data.update({'party': party})
        form = PartyInviteTasterForm(initial=initial_data)

    # use yesterday to filter event so that people can invite more people
    yesterday = timezone.now() - timedelta(days=1)
    if tas_group in u.groups.all():
      parties = Party.objects.filter(partyinvite__invitee=u, event_date__gt=yesterday)
      form.fields['party'].queryset = parties
    elif hos_group in u.groups.all():
      parties = Party.objects.filter(host=u, event_date__gt=yesterday)
      form.fields['party'].queryset = parties
    elif pro_group in u.groups.all():
      parties = Party.objects.filter(organizedparty__pro=u, event_date__gt=yesterday)
      form.fields['party'].queryset = parties

    data["form"] = form
    data["party"] = party
    data["parties_menu"] = True

    return render_to_response("main/party_taster_invite.html", data, context_instance=RequestContext(request))
  else:
    raise PermissionDenied


def resend_rsvp(request):

  email = request.POST.get('email')
  next_url = request.GET.get('next', reverse('home_page'))

  if email:
    user = None
    try:
      user = User.objects.get(email=email)
    except:
      messages.error(request, "There are no upcoming parties that you have been invited to.")
    today = timezone.now()

    invites = InvitationSent.objects.filter(party__event_date__gte=today, guests=user)
    if invites:
      for invite in invites:
        resend_party_invite_email(request, user, invite)
      messages.info(request, "We've resent the invitations for all upcoming parties that you've been invited to. Check your email.")
    else:
      messages.warning(request, "There are no upcoming parties that you have been invited to")
  return HttpResponseRedirect(next_url)


# @login_required

def party_rsvp(request, party_id, rsvp_code=None, response=0):

  data = {}

  u = request.user

  party = get_object_or_404(Party, pk=party_id)

  # if no rsvp_code then user has to login first
  if not rsvp_code and not u.is_authenticated():
    return HttpResponseRedirect(reverse('login') + '?next=' + request.path)

  if u.is_authenticated():
    invite = get_object_or_404(PartyInvite, party=party, invitee=u)
  else:
    invite = get_object_or_404(PartyInvite, party=party, rsvp_code=rsvp_code)
    u = invite.invitee

  # data['rsvp_code'] = rsvp_code
  data['invited_user'] = u

  profile = u.get_profile()

  initial_data = {'party': party, u.userprofile.role(): u}

  if request.POST.get('add_taster'):
    taster_form = PartyInviteTasterForm(request.POST, initial=initial_data)
    form = VerifyEligibilityForm(instance=profile)
    request.user = u
    party_add_taster(request, party, taster_form)
  else:
    taster_form = PartyInviteTasterForm(initial=initial_data)
    form = VerifyEligibilityForm(request.POST or None, instance=profile)

  form.fields['gender'].widget = forms.HiddenInput()

  # signing up as taster
  signup_form = MakeTasterForm(initial={'account_type': 3, 'email': u.email, 'first_name': u.first_name,
                                        'last_name': u.last_name}, instance=u)

  if form.is_valid():
    profile = User.objects.get(id=u.id).get_profile()
    profile.dob = form.cleaned_data['dob']
    profile.save()

  data['signup_form'] = signup_form
  data['taster_form'] = taster_form
  data['form'] = form
  data['age_checked'] = request.GET.get('checked')
  disallow_rsvp = int(response) in [2, 3] and u.get_profile().is_under_age()
  data['disallow_rsvp'] = disallow_rsvp
  # if user has not entered DOB ask them to do this first
  # only validate if response is yes/maybe
  if response:
    if disallow_rsvp and data['age_checked']:
      invite.response = 4
      invite.save()

    if disallow_rsvp == False:
      invite.response = int(response)
      invite.save()

  invitees = PartyInvite.objects.filter(party=party)
  data['questionnaire_completed'] = WineTaste.objects.filter(user=u).exists() and GeneralTaste.objects.filter(user=u).exists()
  data["party"] = party
  data["invitees"] = invitees
  data["invite"] = invite
  data["parties_menu"] = True
  invitations = party.invitationsent_set.all().order_by("-timestamp")
  if invitations.exists():
    data["custom_message"] = invitations[0].custom_message

  sections = ContentTemplate.objects.get(key='rsvp').sections.all()
  content = sections.get(category=0).content
  rsvp_template = Template(content)
  context = RequestContext(request, data)
  page = rsvp_template.render(context)
  data['rsvp_content'] = page

  return render_to_response("main/party_rsvp.html", data, context_instance=RequestContext(request))


@login_required
def party_write_invitation(request, party_id):
  data = {}
  u = request.user

  if u.userprofile.events_manager():
    party = get_object_or_404(Party, id=party_id)
  else:
    party = get_object_or_404(Party, id=party_id, host=u)

  party.setup_stage = 2
  party.save()

  try:
    invitation = InvitationSent.objects.filter(party=party).order_by('-id')[0]
  except:
    invitation = None

  if invitation:
    custom_message = invitation.custom_message if invitation.custom_message else get_default_invite_message(party)
    signature = invitation.signature if invitation.signature else get_default_signature(party)
  else:
    custom_message = get_default_invite_message(party)
    signature = get_default_signature(party)

  initial_data = {'party': party, 'custom_message': custom_message, 'signature': signature, 'custom_subject': "You've been invited to a Vinely Party"}
  form = CustomizeInvitationForm(request.POST or None, initial=initial_data, instance=invitation)

  if request.POST.get("next") or request.POST.get("save") or request.POST.get('preview'):
    if form.is_valid():
      invitation = form.save()
      party = invitation.party
      party.save()

      # messages.success(request, "Your invitation message was successfully saved.")
      if request.POST.get("next"):
        return HttpResponseRedirect(reverse('party_find_friends', args=[party.id]))

      if request.POST.get("save"):
        messages.success(request, "Your invitation message was successfully saved.")
        if party.requested:
          return HttpResponseRedirect(reverse('party_details', args=[party.id]))

      if request.POST.get('preview'):
        # preview = preview_party_invites_email(request, invitation)
        return HttpResponseRedirect(reverse('party_preview_invitation', args=[party.id]))

  data['party'] = party
  data['form'] = form
  data["parties_menu"] = True
  return render_to_response("main/party_customize_invite.html", data, context_instance=RequestContext(request))


@login_required
def party_preview_invitation(request, party_id):
  u = request.user

  data = {}

  if u.userprofile.events_manager():
    party = get_object_or_404(Party, id=party_id)
  else:
    party = get_object_or_404(Party, id=party_id, host=u)

  try:
    invitation = InvitationSent.objects.filter(party=party).order_by('-id')[0]
  except:
    raise Http404

  preview = preview_party_thanks_note_email(request, invitation)
  data['invite_preview'] = preview
  # return HttpResponse(preview)
  return render_to_response("main/party_preview_invitation.html", data, context_instance=RequestContext(request))


@login_required
def party_host_confirmation_preview(request, party_id, email_id):
  u = request.user

  data = {}

  party = get_object_or_404(Party, id=party_id, organizedparty__pro=u)

  email = get_object_or_404(Email, pk=email_id)
  data["party"] = party
  email_template = Template(email.html)
  context = RequestContext(request, data)
  page = email_template.render(context)
  data["preview"] = page

  return render_to_response("main/party_host_confirmation_preview.html", data, context_instance=RequestContext(request))


@login_required
def party_customize_invite(request):
  """
    Customize invitations to those people
  """

  # TODO: show that the following invitation will be sent
  data = {}

  # change RSVP uses same form
  # if request.POST.get('change_rsvp'):
  #   return party_change_taster_rsvp(request)

  if request.method == 'POST':
    guests = request.POST.getlist('guests')
    party = Party.objects.get(id=request.POST.get('party'))
    form = CustomizeInvitationForm()
    host_full_name = "Your friend"
    if request.user.first_name:
      # if inviting person is not the host (a friend of friend or pro)
      host_full_name = "%s %s" % (request.user.first_name, request.user.last_name)
    elif party.host.first_name:
      host_full_name = "%s %s" % (party.host.first_name, party.host.last_name)
    form.initial = {'custom_subject': '%s invites you to a Vinely Party!' % host_full_name,
                    'party': party}
    data["party"] = party
    data["guests"] = guests
    data["form"] = form
    data["guest_count"] = len(guests)
    data["parties_menu"] = True
    data['rsvp_date'] = party.event_date - timedelta(days=5)

    return render_to_response("main/party_customize_invite.html", data, context_instance=RequestContext(request))
  else:
    return PermissionDenied


@login_required
def party_customize_thanks_note(request):
  """
    Customize thank you note by host to attendees
  """
  from cms.models import Section
  data = {}

  if request.method == 'POST':
    guests = request.POST.getlist('guests')
    party = Party.objects.get(id=request.POST.get('party'))

    form = CustomizeThankYouNoteForm()
    form.initial = {'party': party}
    data["party"] = party
    data["guests"] = guests
    data["form"] = form
    data["guest_count"] = len(guests)
    data["parties_menu"] = True
    data['rsvp_date'] = party.event_date - timedelta(days=5)

    template = Section.objects.get(template__key='distribute_party_thanks_note_email', category=0)

    c = RequestContext(request, {'party': party, 'host_name': request.get_host(), 'taster_first_name': 'Taster',
                                'pro_email': party.pro.email, 'placed_order': False, 'show_text_sig': False})

    html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))
    data['not_placed_order'] = html_template.render(c)
    c.update({'placed_order': True})
    data['placed_order'] = html_template.render(c)

    return render_to_response("main/party_customize_thanks_note.html", data, context_instance=RequestContext(request))
  else:
    return PermissionDenied


@login_required
def party_send_thanks_note(request):
  """
    Preview or send thanks note
  """

  data = {}

  # send invitation
  form = CustomizeThankYouNoteForm(request.POST or None)
  if form.is_valid():
    num_guests = len(request.POST.getlist("guests"))
    if form.cleaned_data['preview']:
      note_sent = form.save(commit=False)
      party = note_sent.party
      data["preview"] = True
      data["party"] = party
      data["guests"] = request.POST.getlist("guests")
      data["guest_count"] = num_guests
    else:
      note_sent = form.save()
      party = note_sent.party
      # send e-mails
      guests = request.POST.getlist("guests")
      invitees = PartyInvite.objects.filter(invitee__id__in=guests, party=party).exclude(invitee=party.host)
      orders = Order.objects.filter(cart__party=party)
      buyers = invitees.filter(invitee__in=[x.receiver for x in orders])
      non_buyers = invitees.exclude(invitee__in=[x.receiver for x in orders])
      if non_buyers:
        distribute_party_thanks_note_email(request, note_sent, non_buyers, placed_order=False)
      if buyers:
        distribute_party_thanks_note_email(request, note_sent, buyers, placed_order=True)

      messages.success(request, "Your thank you note was sent successfully to %d Tasters!" % num_guests)
      data["parties_menu"] = True

      return HttpResponseRedirect(reverse("party_details", args=[party.id]))

  data["form"] = form
  data["parties_menu"] = True

  return render_to_response("main/party_preview_thanks_note.html", data, context_instance=RequestContext(request))

# @login_required
# def party_customize_thanks_note(request):
#   """
#     Customize thank you note by host to attendees
#   """

#   data = {}

#   if request.method == 'POST':
#     guests = request.POST.getlist('guests')
#     party = Party.objects.get(id=request.POST.get('party'))
#     #print "Selected guests:", guests

#     form = CustomizeThankYouNoteForm()
#     form.initial = {'party': party}
#     data["party"] = party
#     data["guests"] = guests
#     data["form"] = form
#     data["guest_count"] = len(guests)
#     data["parties_menu"] = True
#     data['rsvp_date'] = party.event_date - timedelta(days=5)

#     return render_to_response("main/party_customize_thanks_note.html", data, context_instance=RequestContext(request))
#   else:
#     return PermissionDenied


@login_required
def party_preview_thanks_note(request, party_id):
  u = request.user

  data = {}

  if u.userprofile.events_manager():
    party = get_object_or_404(Party, id=party_id)
  else:
    party = get_object_or_404(Party, id=party_id, host=u)

  notes = ThankYouNote.objects.filter(party=party)
  if notes.exists():
    thanks_note = notes[0]
  else:
    thanks_note = ThankYouNote.objects.create(party=party)

  preview = preview_party_thanks_note_email(request, thanks_note)
  data['thanks_note_preview'] = preview
  # return HttpResponse(preview)
  return render_to_response("main/party_preview_thanks_note.html", data, context_instance=RequestContext(request))


# @login_required
# def party_send_thanks_note(request, party):
#   """
#     send thanks note
#   """

#   data = {}

#   try:
#     note = ThankYouNote.objects.filter(party=party).order_by('-id')[0]
#   except:
#     note = None

#   # send note
#   form = CustomizeThankYouNoteForm(request.POST or None, instance=note)
#   if form.is_valid():
#     if note:
#       old_note = ThankYouNote.objects.get(pk=note.id)
#     num_guests = len(request.POST.getlist("guests"))
#     note_sent = form.save()
#     if note:
#       note_sent.custom_message = old_note.custom_message
#       note_sent.custom_subject = old_note.custom_subject
#       note_sent.save()
#     party = note_sent.party

#     # send e-mails
#     guests = request.POST.getlist("guests")
#     invitees = PartyInvite.objects.filter(invitee__id__in=guests, party=party).exclude(invitee=party.host)
#     orders = Order.objects.filter(cart__party=party)
#     buyers = invitees.filter(invitee__in=[x.receiver for x in orders])
#     non_buyers = invitees.exclude(invitee__in=[x.receiver for x in orders])
#     if non_buyers:
#       distribute_party_thanks_note_email(request, note_sent, non_buyers, placed_order=False)
#     if buyers:
#       distribute_party_thanks_note_email(request, note_sent, buyers, placed_order=True)

#     messages.success(request, "Your thank you note was sent successfully to %d Tasters!" % num_guests)
#     data["parties_menu"] = True

#     return HttpResponseRedirect(reverse("party_details", args=[party.id]))

#   data["form"] = form
#   data["parties_menu"] = True

#   return HttpResponseRedirect(reverse("party_details", args=[party.id]))


@login_required
def party_send_invites(request):
  """
    Send the invites
  """

  data = {}
  party = get_object_or_404(Party, pk=request.POST.get('party'))

  try:
    invitation = InvitationSent.objects.filter(party=party).order_by('-id')[0]
  except:
    invitation = None

  if request.POST.get('send_thank_you'):
    return party_send_thanks_note(request, party)
  else:
    # send invitation
    form = CustomizeInvitationForm(request.POST or None, instance=invitation)

  if form.is_valid():
    if invitation:
      old_invite = InvitationSent.objects.get(pk=invitation.id)
    num_guests = len(request.POST.getlist("guests"))
    invitation_sent = form.save()
    if invitation:
      invitation_sent.custom_message = old_invite.custom_message
      invitation_sent.custom_subject = old_invite.custom_subject
      invitation_sent.signature = old_invite.signature
      invitation_sent.save()
    party = invitation_sent.party

    # send e-mails
    num_guests = distribute_party_invites_email(request, invitation_sent)
    if num_guests > 0:
      messages.success(request, "Your invitations were sent successfully to %d Tasters!" % num_guests)
      data["parties_menu"] = True

  return HttpResponseRedirect(reverse("party_details", args=[party.id]))


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
def supplier_add_wine(request):
  data = {}
  data["supplier"] = True
  return render_to_response("main/supplier_add_wine.html", data, context_instance=RequestContext(request))


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
def supplier_order_history(request):
  """
  Show order history of fulfilled orders
  """
  return supplier_orders_filter(request, history_list=True)


@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def supplier_all_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  return supplier_orders_filter(request, history_list=False)


def supplier_orders_filter(request, history_list=False):
  sort_field = {
    'order_id': 'id',
    '-order_id': '-id',
    'status': 'fulfill_status',
    '-status': '-fulfill_status',
    'order_date': 'order_date',
    '-order_date': '-order_date',
    'ship_date': 'ship_date',
    '-ship_date': '-ship_date',
    'name': 'ordered_by',
    '-name': '-ordered_by',
    'personality': 'ordered_by__userprofile__wine_personality__name',
    '-personality': '-ordered_by__userprofile__wine_personality__name',
    'rwb': 'order_date',
    '-rwb': '-order_date',
    'quantity': 'cart__items__quantity',
    '-quantity': '-cart__items__quantity',
    'track': 'tracking_number',
    '-track': '-tracking_number',
  }

  u = request.user

  data = {}
  data['supplier_history_view'] = history_list
  data['supplier_all_view'] = not history_list

  # split orders shown by state. Supplier only sees orders to their state
  active_state = None
  if u.email == 'mi_sales@vinely.com':
    active_state = 'MI'
  elif u.email == 'sales@vinely.com':
    active_state = 'MA'

  zipcodes = Zipcode.objects.filter(state=active_state).values('code')

  page_num = request.GET.get('p', 1)
  sort = request.GET.get('sort')
  if sort:
    fld = sort_field.get(sort, '-order_date')
    orders = Order.objects.filter(shipping_address__zipcode__in=zipcodes).order_by(fld)
  else:
    orders = Order.objects.filter(shipping_address__zipcode__in=zipcodes).order_by('-order_date')

  paginator = Paginator(orders, 20)
  try:
    page = paginator.page(page_num)
  except:
    page = paginator.page(1)

  if sort:
    next_page = page.next_page_number() if page.has_next() else page_num
    prev_page = page.previous_page_number() if page.has_previous() else page_num
    first_page_url = urllib.urlencode({'sort': sort})
    last_page_url = urllib.urlencode({'p': paginator.num_pages, 'sort': sort})
    next_page_url = urllib.urlencode({'p': next_page, 'sort': sort})
    prev_page_url = urllib.urlencode({'p': prev_page, 'sort': sort})
  else:
    next_page = page.next_page_number() if page.has_next() else page_num
    prev_page = page.previous_page_number() if page.has_previous() else page_num
    first_page_url = urllib.urlencode({})
    last_page_url = urllib.urlencode({'p': paginator.num_pages})
    next_page_url = urllib.urlencode({'p': next_page})
    prev_page_url = urllib.urlencode({'p': prev_page})

  data['page_count'] = paginator.num_pages
  data['page'] = page
  data['next_page_url'] = next_page_url
  data['prev_page_url'] = prev_page_url
  data['first_page_url'] = first_page_url
  data['last_page_url'] = last_page_url
  data['orders'] = page.object_list
  data['sorting'] = sort

  data["supplier"] = True
  data['supplier_history_view']
  return render_to_response("main/supplier_all_orders.html", data, context_instance=RequestContext(request))


@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def supplier_wine_list(request):
  data = {}
  return render_to_response("main/supplier_wine_list.html", data, context_instance=RequestContext(request))


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

  personality = order.receiver.get_profile().wine_personality

  data['items'] = []
  for item in cart.items.all():
    if item.product.category == 1:
      item.img_file_name = "%s_%s_prodimg.png" % (personality.suffix, item.product.cart_tag)
      # print item.img_file_name
    # TODO: currently template handles tasting kit images
    # elif item.product.category == 0:
    #  item.img_file_name =
    data['items'].append(item)
  data["form"] = form
  data["order_id"] = order_id

  receiver = order.receiver
  data["personality"] = receiver.get_profile().wine_personality
  data["MYSTERY_PERSONALITY"] = WinePersonality.MYSTERY

  try:
    data["customization"] = CustomizeOrder.objects.get(user=order.receiver)
  except CustomizeOrder.DoesNotExist:
    pass

  return render_to_response("main/supplier_edit_order.html", data, context_instance=RequestContext(request))


@login_required
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
  # if u.is_anonymous():
  #   form = ShippingForm(request.POST or None)
  # else:

  if 'receiver_id' in request.session:
    receiver = User.objects.get(id=request.session['receiver_id'])
  else:
    receiver = u

  receiver_profile = receiver.get_profile()

  initial_data = {'first_name': receiver.first_name, 'last_name': receiver.last_name,
                  'email': receiver.email, 'phone': receiver_profile.phone}

  current_shipping = receiver_profile.shipping_address
  if current_shipping:
    initial_data['address1'] = current_shipping.street1
    initial_data['address2'] = current_shipping.street2
    initial_data['company_co'] = current_shipping.company_co
    initial_data['city'] = current_shipping.city
    initial_data['state'] = current_shipping.state
    initial_data['zipcode'] = current_shipping.zipcode
  initial_data['news_optin'] = receiver.get_profile().news_optin

  form = ShippingForm(request.POST or None, instance=receiver, initial=initial_data)
  if not u.get_profile().is_pro() or receiver == u:
    form.fields['email'].widget = forms.HiddenInput()

  age_validity_form = AgeValidityForm(request.POST or None, instance=receiver.get_profile(), prefix='eligibility')

  valid_age = age_validity_form.is_valid()

  data['age_validity_form'] = age_validity_form
  data['form'] = form

  # check zipcode is ok
  if request.method == 'POST':
    zipcode = request.POST.get('zipcode')
    ok = check_zipcode(zipcode)
    if zipcode and not ok:
      messages.error(request, 'Please note that Vinely does not currently operate in the specified area.')
      return render_to_response("main/edit_shipping_address.html", data, context_instance=RequestContext(request))

  if form.is_valid() and valid_age:
    receiver = form.save()

    profile = receiver.get_profile()
    profile.dob = age_validity_form.cleaned_data['dob']
    profile.save()

    # update the receiver user
    request.session['receiver_id'] = receiver.id

    # check if customization exists, if not we need to assign it from the one who's ordering now
    try:
      CustomizeOrder.objects.get(user=receiver)
    except CustomizeOrder.DoesNotExist:
      # customization that current user filled out
      if CustomizeOrder.objects.filter(user=u).exists():
        current_customization = CustomizeOrder.objects.get(user=u)
        new_customization = CustomizeOrder(user=receiver, wine_mix=current_customization.wine_mix, sparkling=current_customization.sparkling)
        new_customization.save()

    # if receiver.is_active is False:
    #   # if new receiving user created.  happens when receiver never attended a party
    #   role = Group.objects.get(name="Vinely Taster")
    #   receiver.groups.add(Group.objects.get(name=role))

    #   temp_password = User.objects.make_random_password()
    #   receiver.set_password(temp_password)
    #   receiver.save()

    #   verification_code = str(uuid.uuid4())
    #   vque = VerificationQueue(user=receiver, verification_code=verification_code)
    #   vque.save()

    #   # send out verification e-mail, create a verification code
    #   send_verification_email(request, verification_code, temp_password, receiver.email)

    if 'ordering' in request.session and request.session['ordering']:
      # only happens when user decided to edit the shipping address
      cart = Cart.objects.get(id=request.session['cart_id'])
      cart.receiver = receiver
      cart.save()
      data["shop_menu"] = True
      return HttpResponseRedirect(reverse("place_order"))
    else:
      # update cart status
      cart = Cart.objects.get(id=request.session['cart_id'])
      cart.status = Cart.CART_STATUS_CHOICES[3][0]
      cart.receiver = receiver
      cart.save()

      if cart.party is None:
        party = None
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

  # data['form'] = form

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

  try:
    receiver = User.objects.get(id=request.session['receiver_id'])
    current_shipping = receiver.get_profile().shipping_address
    receiver_state = Zipcode.objects.get(code=current_shipping.zipcode).state
  except:
    # the receiver has not been specified
    raise PermissionDenied
  data['receiver'] = receiver

  data["receiver_state"] = receiver_state

  # stripe only supported in Michigan
  if receiver_state in Cart.STRIPE_STATES:
    data['use_stripe'] = True

    if request.method == 'POST':
      if receiver_state == 'CA':
        stripe.api_key = settings.STRIPE_SECRET_CA

      stripe_token = request.POST.get('stripe_token')
      stripe_card = receiver.get_profile().stripe_card

      try:
        customer = stripe.Customer.retrieve(id=stripe_card.stripe_user)
        if customer.get('deleted'):
          raise Exception('Customer Deleted')
        stripe_user_id = customer.id

        # makes sure we have the exact same card
        stripe_card = StripeCard.objects.get(stripe_user=stripe_user_id, exp_month=request.POST.get('exp_month'),
                          exp_year=request.POST.get('exp_year'), last_four=request.POST.get('last4'),
                          card_type=request.POST.get('card_type'), billing_zipcode=request.POST.get('address_zip'))
      except:
        # no record of this customer-card mapping so create
        try:
          customer = stripe.Customer.create(card=stripe_token, email=receiver.email)
          stripe_user_id = customer.id

          # create on vinely
          stripe_card, created = StripeCard.objects.get_or_create(stripe_user=stripe_user_id, exp_month=request.POST.get('exp_month'),
                                    exp_year=request.POST.get('exp_year'), last_four=request.POST.get('last4'),
                                    card_type=request.POST.get('card_type'), billing_zipcode=request.POST.get('address_zip'))
          if created:
            profile = receiver.get_profile()
            profile.stripe_card = stripe_card
            profile.save()
            profile.stripe_cards.add(stripe_card)

        except:
          messages.error(request, 'Your card was declined. In case you are in testing mode please use the test credit card.')
          return HttpResponseRedirect('.')

      # update cart status
      cart = Cart.objects.get(id=request.session['cart_id'])
      cart.status = Cart.CART_STATUS_CHOICES[4][0]
      cart.save()
      request.session['stripe_payment'] = True

      # go finalize order
      data["shop_menu"] = True
      return HttpResponseRedirect(reverse("place_order"))

  else:
    # other states use Processed through Vinely - MA
    form = PaymentForm(request.POST or None)

    if form.is_valid():
      new_card = form.save()
      profile = receiver.get_profile()
      profile.credit_card = new_card
      profile.save()

      # update cart status
      cart = Cart.objects.get(id=request.session['cart_id'])
      cart.status = Cart.CART_STATUS_CHOICES[4][0]
      cart.save()

      # for now save the card to receiver
      profile.credit_cards.add(new_card)
      request.session['stripe_payment'] = False

      # go finalize order
      data["shop_menu"] = True
      return HttpResponseRedirect(reverse("place_order"))

    # display form: prepopulate with previous credit card used
    current_user_profile = receiver.get_profile()
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

  if receiver_state == 'CA':
    data['publish_token'] = settings.STRIPE_PUBLISHABLE_CA

  data["shop_menu"] = True
  return render_to_response("main/edit_credit_card.html", data, context_instance=RequestContext(request))


@login_required
def cart_kit_detail(request, kit_id):
  kit = Product.objects.get(id=int(kit_id))
  data = {}
  #data['description'] = kit.description
  data['price'] = "%s" % kit.unit_price  # TODO: is there a better way to serialize currency
  data['product'] = kit.name
  return HttpResponse(json.dumps(data), mimetype="application/json")


@login_required
def cart_quantity(request, level, quantity):
  '''
  Quantity:
  1 = 3 bottles
  2 = 6 bottles
  3 = 12 bottles
  '''
  data = {}
  quantity = int(quantity)

  if quantity == 1:
    name = "3 Bottles"
  elif quantity == 2:
    name = "6 Bottles"
  elif quantity == 3:
    name = "12 Bottles"

  try:
    product = Product.objects.get(cart_tag=level, name=name)
  except Product.DoesNotExist:
    # not a valid product
    raise Http404

  data['price'] = "%.2f" % product.unit_price

  return HttpResponse(json.dumps(data), mimetype="application/json")


@login_required
def party_select(request):
  """
    Show upcoming parties
  """

  u = request.user

  data = {}

  today = timezone.now()

  # check if there's a party that has not ordered a kit, exclude completed orders
  parties = Party.objects.filter(host=u, event_date__gte=today)
  cart = Cart.objects.filter(user=u, party__in=parties, status=Cart.CART_STATUS_CHOICES[5][0])
  parties = parties.exclude(id__in=[x.party.id for x in cart])
  data['parties'] = parties
  data["parties_menu"] = True

  return render_to_response("main/party_select.html", data, context_instance=RequestContext(request))


import cStringIO
from pyPdf import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.contrib import staticfiles
from urllib2 import urlopen
import string
import os, zipfile
# from django.core.servers.basehttp import FileWrapper


def generate_rating_card(event_date, pro, host, invitee, in_stream, output):
    """
      internal method used to generate rating card for each invitee
    """

    packet = cStringIO.StringIO()
    exp_doc = PdfFileReader(in_stream)
    # output = PdfFileWriter()

    can = canvas.Canvas(packet, pagesize=letter)
    # Taster name
    can.setFont('Helvetica-Bold', 12)
    can.drawString(230, 74, string.upper(invitee.get_full_name()))
    can.drawString(630, 74, string.upper(invitee.get_full_name()))

    can.setFont('Courier', 9)
    # event date
    can.drawString(230, 63, event_date)
    can.drawString(630, 63, event_date)
    # host name
    can.drawString(230, 53, host.get_full_name())
    can.drawString(630, 53, host.get_full_name())
    # pro name
    can.drawString(230, 43, pro.get_full_name())
    can.drawString(630, 43, pro.get_full_name())
    can.save()

    packet.seek(0)
    text = PdfFileReader(packet)

    for x in range(exp_doc.numPages):
      page = exp_doc.getPage(x)
      page.mergePage(text.getPage(0))
      output.addPage(page)

    # when creating multiple files
    # filename = CARDS_PATH + invite.invitee.email+ '.pdf'
    # with file(filename, 'wb') as out_stream:
    #   output.write(out_stream)
    # files.append(filename)


@login_required
def print_rating_cards(request, party_id):

  party = get_object_or_404(Party, id=party_id)
  invites = PartyInvite.objects.filter(party=party)
  if invites.count() == 0:
    messages.warning(request, "No guests have been invited to the party. Invite guests first.")
    return HttpResponseRedirect(reverse("party_details", args=[party_id]))

  # assume whoever is printing this is the pro
  pro = request.user
  host = party.host
  event_date = party.event_date.strftime('%m-%d-%Y')

  path = staticfiles.templatetags.staticfiles.static("doc/PDF_vinely_experience_card_Raw.pdf")

  if path.startswith('http'):
    static_p = urlopen(path)
    in_stream = cStringIO.StringIO(static_p.read())
  else:
    path = settings.PROJECT_ROOT + '/static' + '/doc/PDF_vinely_experience_card_Raw.pdf'
    in_stream = file(path, 'rb')

  # with file(path, 'rb') as in_stream:
  CARDS_PATH = 'Vinely_experience_cards/'
  if not os.path.exists(CARDS_PATH):
    os.mkdir(CARDS_PATH)

  # when creating multiple files, uncomment the following line
  # files = []
  output = PdfFileWriter()
  # generate rating card for host
  generate_rating_card(event_date, pro, host, host, in_stream, output)
  for invite in invites:
    # generate rating cards for invitees
    if invite.invitee != host:
      generate_rating_card(event_date, pro, host, invite.invitee, in_stream, output)

  ratings_zip = CARDS_PATH + 'ratings-%s.zip' % pro.email

  # with zipfile.ZipFile(ratings_zip, 'w') as myzip:
  #   for f in files:
  #     myzip.write(f, compress_type=zipfile.ZIP_DEFLATED)

  # # delete the temp pdf files
  # for f in files:
  #   try:
  #     os.remove(f)
  #   except:
  #     pass
  ratings_pdf = CARDS_PATH + 'experience_cards-%s.pdf' % pro.email
  with file(ratings_pdf, 'wb') as out_stream:
    output.write(out_stream)

  with zipfile.ZipFile(ratings_zip, 'w') as myzip:
    myzip.write(ratings_pdf, compress_type=zipfile.ZIP_DEFLATED)

  os.unlink(ratings_pdf)

  in_stream.close()
  f = file(ratings_zip, 'r')
  response = HttpResponse(f, content_type='application/zip')
  response['Content-Disposition'] = 'attachment; filename=Vinely_experience_cards.zip'
  return response
  # return HttpResponseRedirect()


################################################################################
#
# Vinely Hosted Event views
#
################################################################################

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def fb_vinely_event(request):
  return vinely_event(request, fb_page=1)


def vinely_event(request, fb_page=0):
  data = {}
  data['fb_view'] = fb_page
  content = ContentTemplate.objects.get(key='vinely_event').sections.all()[0].content
  # have to render to template first because of template tags
  event_template = Template(content)
  context = RequestContext(request, data)
  page = event_template.render(context)
  data['event_content'] = page

  return render_to_response("main/vinely_event.html", data, context)


def fb_vinely_event_signup(request, party_id):
  return vinely_event_signup(request, party_id, 1)


def vinely_event_signup(request, party_id, fb_page=0):
  # Allow taster to signup from FB page
  # if signing up as a taster there must be a party to link to
  u = request.user

  account_type = 3
  role = Group.objects.get(id=account_type)
  data = {}
  data['fb_view'] = fb_page
  today = timezone.now()

  if u.userprofile.events_manager():
    party = get_object_or_404(Party, pk=party_id)
  else:
    party = get_object_or_404(Party, pk=party_id, event_date__gte=today)

  verification_code = ''
  temp_password = ''

  # create users and send e-mail notifications
  form = EventSignupForm(request.POST or None, initial={'account_type': account_type, 'vinely_event': True})

  if form.is_valid():
    # if user already exists just add them to the event dont save
    try:
      user = User.objects.get(email=request.POST.get('email').strip().lower())
      profile = user.get_profile()
      profile.zipcode = form.cleaned_data['zipcode']
      profile.save()
    except User.DoesNotExist:
      user = form.save()
      profile = user.get_profile()
      profile.zipcode = form.cleaned_data['zipcode']
      profile.save()
      user.groups.add(role)
      user.is_active = False
      temp_password = User.objects.make_random_password()
      user.set_password(temp_password)
      user.save()

      # save engagement type
      engagement_type = account_type

      interest, created = EngagementInterest.objects.get_or_create(user=user,
                                                        engagement_type=engagement_type)

      verification_code = str(uuid.uuid4())
      vque = VerificationQueue(user=user, verification_code=verification_code)
      vque.save()

      # send out verification e-mail, create a verification code
      # send_verification_email(request, verification_code, temp_password, user.email)

    data["email"] = user.email
    data["first_name"] = user.first_name
    data["account_type"] = account_type

    try:
      response = int(request.POST['rsvp'])
    except ValueError:
      if "Yes" in request.POST['rsvp']:
        response = 3
      elif "No" in request.POST['rsvp']:
        response = 1
      elif "Maybe" in request.POST['rsvp']:
        response = 2

    # link them to party and RSVP
    # check if already RSVP'ed and just changed response if needed
    try:
      invite = PartyInvite.objects.get(party=party, invitee=user)
      invite.response = response
      invite.response_timestamp = today
      invite.save()
    except PartyInvite.DoesNotExist:
      # if doest exist then create
      PartyInvite.objects.create(party=party, invitee=user, invited_by=party.host,
                                response=response, response_timestamp=today)
    if response == 1:
      # msg = 'We hope you will be able to attend next time. You can always visit to our website in case change your mind.'
      data['attending'] = False
    else:
      # msg = "Thank you for your interest in attending a Vinely Party."
      data['attending'] = True

      ok = check_zipcode(profile.zipcode)
      if profile.zipcode and not ok:
        messages.info(request, 'Please note that Vinely does not currently operate in your area.')
        send_not_in_area_party_email(request, user, account_type)
      send_rsvp_thank_you_email(request, user, verification_code, temp_password)
    # messages.success(request, msg)

    if u.userprofile.events_manager():
      return HttpResponseRedirect(reverse('party_details', args=[party.id]))
    else:
      return render_to_response("main/vinely_event_rsvp_sent.html", data, context_instance=RequestContext(request))

  # data['heard_about_us_form'] = HeardAboutForm()
  data['form'] = form
  data['role'] = role.name
  data['account_type'] = account_type
  data["get_started_menu"] = True

  return render_to_response("main/vinely_event_signup.html", data, context_instance=RequestContext(request))
