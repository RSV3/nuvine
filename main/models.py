from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django.core.urlresolvers import reverse

from accounts.models import Address, CreditCard, SubscriptionInfo
from personality.models import WineRatingData
from sorl.thumbnail import ImageField

from datetime import datetime, timedelta
from stripecard.models import StripeCard
import uuid

# Create your models here.


class ContactReason(models.Model):
  reason = models.CharField(max_length=1024)

  def __unicode__(self):
    return self.reason


class ContactRequest(models.Model):

  SEX_CHOICES = (
      (0, 'Female'),
      (1, 'Male'),
      (2, 'Neither'),
  )

  subject = models.ForeignKey(ContactReason)
  first_name = models.CharField(max_length=64)
  last_name = models.CharField(max_length=64, null=True, blank=True)
  sex = models.IntegerField(choices=SEX_CHOICES, default=SEX_CHOICES[0][0])
  email = models.EmailField(verbose_name="E-mail", unique=True)
  phone = models.CharField(max_length=16, null=True, blank=True)
  message = models.TextField()
  zipcode = models.CharField(max_length=12)


class Party(models.Model):

  # default to the name of the host
  host = models.ForeignKey(User)
  title = models.CharField(max_length=128)
  description = models.TextField(verbose_name="Special Instructions")
  address = models.ForeignKey(Address)
  phone = models.CharField(max_length=16, verbose_name="Contact phone number", null=True, blank=True)
  created = models.DateTimeField(auto_now_add=True)
  event_date = models.DateTimeField()
  auto_invite = models.BooleanField()
  auto_thank_you = models.BooleanField()
  guests_can_invite = models.BooleanField()
  guests_see_guestlist = models.BooleanField()
  confirmed = models.BooleanField()
  requested = models.BooleanField()
  setup_stage = models.IntegerField(default=1)

  class Meta:
    verbose_name_plural = 'Parties'

  def __unicode__(self):
    if self.host.first_name:
      return "%s by %s <%s>" % (self.title, self.host.first_name, self.host.email)
    else:
      return "%s by <%s>" % (self.title, self.host.email)

  def party_setup_url(self):
    url = 'party_details'
    if not self.requested and not self.confirmed:
      if self.setup_stage == 1:
        url = 'party_add'
      elif self.setup_stage == 2:
        url = 'party_write_invitation'
      elif self.setup_stage == 3:
        url = 'party_find_friends'
      elif self.setup_stage == 4:
        url = 'party_review_request'
    return reverse(url, args=[self.id])

  @property
  def pro(self):
    try:
      return OrganizedParty.objects.get(party=self).pro
    except OrganizedParty.DoesNotExist:
      return None

  def is_past_party(self):
    party_valid_date = timezone.now() - timedelta(hours=24)
    return self.event_date < party_valid_date

  def kit_ordered(self):
    order = Order.objects.filter(cart__party=self, cart__items__product__category=Product.PRODUCT_TYPE[0][0])
    return order.exists()

  def invite_sent(self):
    return PartyInvite.objects.filter(party=self).exists()

  def high_low(self):
    coming = PartyInvite.objects.filter(party=self, response__in=[2, 3]).count()
    if coming < 8:
      return '!LOW'
    elif coming > 24:
      return '!HIGH'
    else:
      return ''

  def invitees(self):
    invites = PartyInvite.objects.filter(party=self).count()
    coming = PartyInvite.objects.filter(party=self, response__in=[2, 3]).count()

    if invites == 0:
      return "0 [0]"
    else:
      return "%d [%d]" % (coming, invites)

  def num_orders(self):
    # TODO: num orders and num orders pending
    return "%d [%d]" % (5, 4)

  def credit(self):
    order_window = self.event_date + timedelta(days=7)
    total_orders = 0
    orders = Order.objects.filter(cart__party=self, order_date__lte=order_window)
    # exclude orders made by host
    orders = orders.exclude(ordered_by=self.host)
    # should not be tasting kit
    orders = orders.exclude(cart__items__product__category=Product.PRODUCT_TYPE[0][0])
    aggregate = orders.aggregate(total=Sum('cart__items__total_price'))
    total_orders += aggregate['total'] if aggregate['total'] else 0

    # sales < 399 = 0 credit
    # 400 - 599 = 40
    # 600 - 799 = 60
    # 800 - 999 = 90
    # 1000-1199 = 120
    # 1200-1399 = 150
    credit = 20

    total = int(total_orders + 1)
    for cost in range(400, total, 200):
      if cost == 400:
        credit += 40
      elif cost > 800:
        credit += 30
      else:
        credit += 20

    return credit

  def pro_commission(self):
    orders = Order.objects.filter(cart__party=self)
    # exclude taste kits
    orders = orders.exclude(cart__items__product__category=Product.PRODUCT_TYPE[0][0])

    # get one-time basic orders
    one_time_basic = orders.filter(cart__items__frequency=SubscriptionInfo.FREQUENCY_CHOICES[0][0], cart__items__price_category__in=[5, 6])
    # get one-time divine, superior
    one_time_other = orders.filter(cart__items__frequency=SubscriptionInfo.FREQUENCY_CHOICES[0][0], cart__items__price_category__in=[7, 8, 9, 10])
    # get frequency buys
    freq_orders = orders.filter(cart__items__frequency__in=[1, 2, 3])

    basic_total = other_total = freq_total = 0
    basic_aggr = one_time_basic.aggregate(total=Sum('cart__items__total_price'))
    basic_total += basic_aggr['total'] if basic_aggr['total'] else 0
    other_aggr = one_time_other.aggregate(total=Sum('cart__items__total_price'))
    other_total += other_aggr['total'] if other_aggr['total'] else 0
    freq_aggr = freq_orders.aggregate(total=Sum('cart__items__total_price'))
    freq_total += freq_aggr['total'] if freq_aggr['total'] else 0
    return (0.1 * float(basic_total)) + (0.125 * float(other_total)) + (0.125 * float(freq_total))


class PartyInvite(models.Model):

  RESPONSE_CHOICES = (
      (0, 'No Answer'),
      (1, 'No'),
      (2, 'Maybe'),
      (3, 'Yes'),
      (4, 'Under Age'),
  )

  party = models.ForeignKey(Party, verbose_name="Taste Party")
  invitee = models.ForeignKey(User, related_name="my_invites", verbose_name="Select Taster")
  # if other than the host
  invited_by = models.ForeignKey(User, related_name="my_guests", blank=True, null=True)
  response = models.IntegerField(choices=RESPONSE_CHOICES, default=RESPONSE_CHOICES[0][0])
  invited_timestamp = models.DateTimeField(blank=True, null=True)  # auto_now_add=True)
  response_timestamp = models.DateTimeField(blank=True, null=True)
  rsvp_code = models.CharField(max_length=64, blank=True, null=True)

  def invited(self):
    return bool(self.invited_timestamp)

  def set_response(self, response):
    self.response = response
    self.response_timestamp = datetime.now()
    self.save()

  def __unicode__(self):
    if self.invited_by:
      return "%s invited by %s to %s" % (self.invitee.email, self.invited_by.email, self.party.title)
    else:
      return "%s invited to %s" % (self.invitee.email, self.party.title)


class PersonaLog(models.Model):
  """
    First party that a person's personality was saved
  """
  user = models.OneToOneField(User, related_name="personality_found")
  #: party and Pro's are null if user created their own personality
  party = models.ForeignKey(Party, null=True)
  pro = models.ForeignKey(User, null=True, related_name="personality_acquired")
  timestamp = models.DateTimeField(auto_now_add=True)


class Product(models.Model):

  # NOTE: If you change product type, please update main/views.py cart()
  PRODUCT_TYPE = (
      (0, 'Tasting Kit'),
      (1, 'Wine Package'),
      (2, 'Wine Bottle'),
  )

  BASIC = "basic"
  SUPERIOR = "superior"
  DIVINE = "divine"

  name = models.CharField(max_length=128)
  sku = models.CharField(max_length=32, default="xxxxxxxxxxxxxxxxxxxxxxxxxx")
  category = models.IntegerField(choices=PRODUCT_TYPE, default=PRODUCT_TYPE[0][0])
  description = models.CharField(max_length=1024)
  #: half case price
  unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
  full_case_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

  image = ImageField(upload_to="products/")
  cart_tag = models.CharField(max_length=64, default="x")
  active = models.BooleanField(default=True)
  # when it was last added
  timestamp = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "%s - $ %s" % (self.name, self.unit_price)
    # return "%s" % (self.name)


class LineItem(models.Model):

  # Make sure some of these values are same in
  # accounts.models.py SubscriptionInfo.QUANTITY_CHOICES
  PRICE_TYPE = (
      (0, 'Product'),
      (1, 'Service'),
      (2, 'Sales Tax'),
      (3, 'Shipping'),
      (4, 'Discount'),
      (5, 'Basic: Full Case (12 bottles)'),
      (6, 'Basic: Half Case (6 bottles)'),
      (7, 'Superior: Full Case (12 bottles)'),
      (8, 'Superior: Half Case (6 bottles)'),
      (9, 'Divine: Full Case (12 bottles)'),
      (10, 'Divine: Half Case (6 bottles)'),
      (11, 'Host Tasting Kit'),
      (12, '3 Bottles'),
      (13, '6 Bottles'),
      (14, '12 Bottles'),

  )

  product = models.ForeignKey(Product, null=True)
  price_category = models.IntegerField(choices=PRICE_TYPE, default=PRICE_TYPE[0][0])
  # NOTE: quantity: legacy from old code - 1 is full case, 2 is half case for wines
  #                 for tasting kits 1 is 6 bottles, 2 is 12 bottles total
  quantity = models.IntegerField(default=1)
  frequency = models.IntegerField(choices=SubscriptionInfo.FREQUENCY_CHOICES, default=1)
  total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

  def __unicode__(self):
    return "%s - %s - %s" % (self.product, self.get_price_category_display(), self.get_frequency_display())

  def subtotal(self):
    if self.price_category in [5, 7, 9]:
      #return 2*float(self.product.unit_price)
      return self.product.full_case_price
    elif self.price_category in [6, 8, 10]:
      return self.product.unit_price
    else:
      return self.quantity * self.product.unit_price

  def quantity_str(self):
    if self.price_category in [5, 6, 7, 8, 9, 10]:
      return "Full Case" if self.quantity == 1 else "Half Case"
    elif self.price_category in [12, 13, 14]:
      return self.product.name
    else:
      return str(self.quantity)


class Cart(models.Model):
  """
    All orders added up
  """
  user = models.ForeignKey(User, null=True)
  items = models.ManyToManyField(LineItem)
  updated = models.DateTimeField(auto_now=True)
  # need receiver to calculate taxing
  receiver = models.ForeignKey(User, null=True, related_name="receiver")

  # to track the parties that resulted in orders
  party = models.ForeignKey(Party, null=True)

  CART_STATUS_CHOICES = (
      (0, 'STARTED'),
      (1, 'ADDED ITEM'),
      (2, 'CUSTOMIZED CHECKOUT'),
      (3, 'FILLED SHIPPING'),
      (4, 'FILLED BILLING'),
      (5, 'COMPLETED ORDER'),
  )

  NO_TAX_STATES = ('MA',)

  STRIPE_STATES = ('MI', 'CA')

  status = models.IntegerField(choices=CART_STATUS_CHOICES, default=0)

  # tracks activity in the carts
  adds = models.IntegerField(default=0)
  removes = models.IntegerField(default=0)
  # viewing cart
  views = models.IntegerField(default=0)

  def subtotal(self):
    # sum of all line items
    price_sum = 0
    for o in self.items.all():
      price_sum += float(o.subtotal())
    return price_sum

  def shipping(self):
    # NOTE: Quantity has different interpretations depending on if wine case or tasting kit
    #
    # For Wine case quantity means:
    # 1 = full case
    # 2 = half case
    #
    # For tasting kit quantity is the number if kits ordered

    # Subscriptions get free shipping
    STANDARD_SHIPPING = 15.95

    shipping = 0
    for item in self.items.all():
      # tasting kits
      if item.price_category == 11:
        shipping += STANDARD_SHIPPING * item.quantity

      if item.price_category == 14 and item.frequency != 1:
        shipping += STANDARD_SHIPPING

    quarter_case_count = self.items.filter(price_category=12).exclude(frequency=1).count()
    half_case_count = self.items.filter(price_category=13).exclude(frequency=1).count()
    case_count = (quarter_case_count * 3) + (half_case_count * 6)
    x = case_count / 12
    y = case_count % 12
    if y == 0:
      ship = x * STANDARD_SHIPPING
    else:
      ship = (x + 1) * STANDARD_SHIPPING
    shipping += ship

    return shipping

  def tax(self):
    if self.receiver and self.receiver.get_profile().shipping_address.state in self.NO_TAX_STATES:
        tax = 0
    elif self.user and self.user.get_profile().shipping_address.state in self.NO_TAX_STATES:
        tax = 0
    else:
      tax = float(self.subtotal()) * 0.06
    return tax

  def total(self):
    return self.shipping() + self.tax() + self.subtotal()

  def items_str(self):
    output = []
    for item in self.items.all():
      output.append(item.product)

    return str(output)

  def __unicode__(self):
    return self.items_str()


class Order(models.Model):
  """
    An order is created when a user finally pays for the order

    The orders also indicate how frequently it will be fulfilled
  """
  ordered_by = models.ForeignKey(User, related_name="ordered")
  receiver = models.ForeignKey(User, related_name="received")
  # unique order id
  order_id = models.CharField(max_length=128)
  cart = models.OneToOneField(Cart)
  shipping_address = models.ForeignKey(Address, null=True)
  credit_card = models.ForeignKey(CreditCard, null=True)
  stripe_card = models.ForeignKey(StripeCard, null=True)
  order_date = models.DateTimeField(auto_now_add=True)

  FULFILL_CHOICES = (
      (0, 'Not Ordered'),
      (1, 'Ordered'),
      (2, 'Processing'),
      (3, 'Delayed'),
      (4, 'Out of Stock'),
      (5, 'Wine Selected'),
      (6, 'Shipped'),
      (7, 'Received'),
  )
  fulfill_status = models.IntegerField(choices=FULFILL_CHOICES, default=0)

  CARRIER_TYPE = (
      (0, 'Unspecified'),
      (1, 'FedEx'),
      (2, 'UPS'),
      (3, 'DHL'),
      (4, 'USPS')
  )
  carrier = models.IntegerField(choices=CARRIER_TYPE, default=0)
  tracking_number = models.CharField(max_length=128, null=True, blank=True)
  ship_date = models.DateTimeField(blank=True, null=True)
  last_updated = models.DateTimeField(auto_now=True)

  def vinely_order_id(self):
    return 'OR' + str(self.id).zfill(7)

  def assign_new_order_id(self):
    new_order_id = str(uuid.uuid4())
    self.order_id = new_order_id
    self.save()
    return new_order_id

  def receiver_personality(self):
    """
      return wine personality of receiver
    """
    profile = self.receiver.get_profile()
    if profile.wine_personality:
      return profile.wine_personality.name
    else:
      return "-"

  def quantity_summary(self):
    items = self.cart.items.filter(price_category__in=[5, 6, 7, 8, 9, 10])
    if items.exists():
      return items[0].quantity_str()
    else:
      items = self.cart.items.exclude(price_category__in=[5, 6, 7, 8, 9, 10])
      if items.exists():
        return items[0].quantity
    return "-"

  def recurring(self):
    items = self.cart.items.filter(frequency__in=[1, 2, 3])
    if items.exists():
      return "Y"
    else:
      return "N"

  def party_state(self):
    # find the party state by looking at the party that the receiver has participated
    latest_parties = PartyInvite.objects.filter(invitee=self.receiver).order_by('-party__event_date')
    if latest_parties.exists():
      return latest_parties[0].party.address.state
    else:
      # if no party exists, it probably means that the guest is ordering for someone else
      latest_parties = PartyInvite.objects.filter(invitee=self.ordered_by).order_by('-party__event_date')
      if latest_parties.exists():
        return latest_parties[0].party.address.state
      else:
        # there is an issue finding out which party this order belongs to
        return "-"

  def ships_to(self):
    return self.shipping_address.state


class OrderReview(models.Model):
  """
    One order review per wine
    Multiple order review per order
  """
  user = models.ForeignKey(User)
  order = models.ForeignKey(Order)
  wine_rating = models.ForeignKey(WineRatingData)
  timestamp = models.DateTimeField(auto_now_add=True)


class OrganizedParty(models.Model):
  """
    Recorded when a party is organized by a pro
  """
  pro = models.ForeignKey(User, null=True, blank=True)
  party = models.ForeignKey(Party)
  timestamp = models.DateTimeField(auto_now_add=True)


class MyHost(models.Model):
  """
    Shows the hosts that are assigned to a party pro
    Currently logs all historicall assignment and uses the latest
    assignment
  """
  pro = models.ForeignKey(User, related_name="my_host", null=True, blank=True, verbose_name="Select Pro")
  host = models.ForeignKey(User, related_name="my_pro")
  # email of a pro or mentor that user entered, that does not map to existing pro
  email_entered = models.CharField(max_length=75, blank=True, null=True, verbose_name="Pro Email Entered")
  timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Host Request Date")

  def __unicode__(self):
    return "%s - %s" % (self.pro, self.host)


class CustomizeOrder(models.Model):
  user = models.ForeignKey(User, null=True)

  MIX_CHOICES = (
    (0, 'Your Vinely recommendation'),
    (1, 'Send me a mix of red & white wine'),
    (2, 'Send me red wine only'),
    (3, 'Send me white wine only')
      # (1, 'Both'),
      # (2, 'Red'),
      # (3, 'White')
  )

  wine_mix = models.IntegerField(choices=MIX_CHOICES, verbose_name="Tell us a little more about what you would like in your shipment.",
                                  default=MIX_CHOICES[0][0])

  SPARKLING_CHOICES = (
      (0, 'No thanks'),
      (1, 'Yes')
  )

  sparkling = models.IntegerField(choices=SPARKLING_CHOICES, verbose_name="Can we include sparkling wine?",
                                    default=SPARKLING_CHOICES[0][0])
  timestamp = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

  def __unicode__(self):
    return "Mix: %s, Sparkling: %s" % (self.get_wine_mix_display(), self.get_sparkling_display())


class EngagementInterest(models.Model):
  """
    Interest in becoming party pro or hosts or tasters attending party
  """

  ENGAGEMENT_CHOICES = (
    (0, 'Unassigned Interest'),
    (1, 'Vinely Pro'),
    (2, 'Vinely Host'),
    (3, 'Vinely Taster'),
    (4, 'Unassigned Interest'),
    (5, 'Tasting Kit'),
    (6, 'Hosting Party'),
  )

  user = models.ForeignKey(User)
  engagement_type = models.IntegerField(choices=ENGAGEMENT_CHOICES, default=ENGAGEMENT_CHOICES[0][0])
  latest = models.DateTimeField(auto_now=True)
  timestamp = models.DateTimeField(auto_now_add=True)

  def update_time(self):
    self.latest = datetime.now()
    self.save()

  def __unicode__(self):
    return "%s interest in %s" % (self.user.email, EngagementInterest.ENGAGEMENT_CHOICES[self.engagement_type][1])


class InvitationSent(models.Model):
  """
    Tracking the invitations sent from Party Details page
  """
  party = models.ForeignKey(Party)
  custom_subject = models.CharField(max_length=128, default="You're invited to a Vinely Party!")
  custom_message = models.CharField(max_length=1024, blank=True, null=True)
  signature = models.CharField(max_length=1024, blank=True, null=True)
  guests = models.ManyToManyField(User, blank=True, null=True)
  timestamp = models.DateTimeField(auto_now_add=True)


class ThankYouNote(models.Model):
  """
  """
  party = models.ForeignKey(Party)
  custom_subject = models.CharField(max_length=128, default="Thanks for Attending My Vinely Taste Party!")
  custom_message = models.CharField(max_length=1024, blank=True, null=True)
  guests = models.ManyToManyField(User)
  timestamp = models.DateTimeField(auto_now_add=True)


class ProSignupLog(models.Model):

  new_pro = models.ForeignKey(User)
  mentor = models.ForeignKey(User, blank=True, null=True, related_name="new_mentees")
  mentor_email = models.CharField(max_length=75, blank=True, null=True, verbose_name="Typed Mentor Email")
  timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Pro Request Date")


class NewHostNoParty(models.Model):
  host = models.ForeignKey(User)


class UnconfirmedParty(models.Model):
  party = models.ForeignKey(Party)

# class SupplierWine(models.Model):
#   '''
#   This stores the wine casings for suppliers
#   '''
#   WINE_COLOR = (
#     (0, "Red"),
#     (1, "Rose"),
#     (2, "White")
#   )
#   SWEETNESS = (

#   )
#   name = models.CharField(max_length=128)
#   sku = models.CharField(max_length=32, default="xxxxxxxxxxxxxxxxxxxxxxxxxx")
#   winery = models.CharField(max_length=128)
#   color =  models.IntegerField(choices=WINE_COLOR)
#   sparkling = models.BooleanField()
#   varietal = models.CharField(max_length=128)
#   vintage = models.IntegerField()
#   category = models.IntegerField(choices=PRODUCT_TYPE, default=PRODUCT_TYPE[0][0])
#   timestamp = models.DateTimeField(auto_now_add=True)
