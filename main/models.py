from django.db import models
from django.contrib.auth.models import User

from accounts.models import Address, CreditCard, SubscriptionInfo
from personality.models import WineRatingData
from sorl.thumbnail import ImageField

from datetime import date, datetime, timedelta

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

  # default to the name of the socializer
  socializer = models.ForeignKey(User)
  title = models.CharField(max_length=128)
  description = models.TextField(verbose_name="Special Instructions")
  address = models.ForeignKey(Address)
  phone = models.CharField(max_length=16, verbose_name="Contact phone number", null=True, blank=True)
  created = models.DateTimeField(auto_now_add=True)
  event_date = models.DateTimeField()

  def __unicode__(self):
    return self.title

  def invitees(self):
    invites = PartyInvite.objects.filter(party=self).count()
    coming = PartyInvite.objects.filter(party=self, response__in=[2,3]).count()

    if invites == 0:
      return ""
    else:
      return "%d [%d]"%(coming, invites)

  def num_orders(self):
    # TODO: num orders and num orders pending 
    return "%d [%d]"%(5, 4) 

  def credit(self):
    # TODO: determines the dollar amount purchased at the party
    return 54.99

class PartyInvite(models.Model):

  RESPONSE_CHOICES = (
      (0, 'No Answer'),
      (1, 'No'),
      (2, 'Maybe'),
      (3, 'Yes')
  )

  party = models.ForeignKey(Party, verbose_name="Taste Party")
  invitee = models.ForeignKey(User, related_name="my_invites", verbose_name="Select Taster")
  # if other than the socializer
  invited_by = models.ForeignKey(User, related_name="my_guests", blank=True, null=True)
  response = models.IntegerField(choices=RESPONSE_CHOICES, default=RESPONSE_CHOICES[0][0])
  invited_timestamp = models.DateTimeField(auto_now_add=True)
  response_timestamp = models.DateTimeField(blank=True, null=True)

  def set_response(self, response):
    self.response = response
    self.response_timestamp = datetime.now()
    self.save()

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
  PRODUCT_TYPE = (
      (0, 'Tasting Kit'),
      (1, 'Wine Package'),
      (2, 'Wine Bottle'),
  )

  name = models.CharField(max_length=128)
  sku = models.CharField(max_length=32, default="xxxxxxxxxxxxxxxxxxxxxxxxxx")
  category = models.IntegerField(choices=PRODUCT_TYPE, default=PRODUCT_TYPE[0][0])
  description = models.CharField(max_length=1024)
  unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
  image = ImageField(upload_to="products/")
  cart_tag = models.CharField(max_length=64, default="x")
  active = models.BooleanField(default=True)
  # when it was last added 
  timestamp = models.DateTimeField(auto_now_add=True)

class LineItem(models.Model):

  PRICE_TYPE = (
      (0, 'Product'),
      (1, 'Service'),
      (2, 'Sales Tax'),
      (3, 'Shipping'),
      (4, 'Discount'),
      (5, 'Basic: Full Case (12 bottles)'),
      (6, 'Basic: Half Case (6 bottles)'),
      (7, 'Classic: Full Case (12 bottles)'),
      (8, 'Classic: Half Case (6 bottles)'),
      (9, 'Divine: Full Case (12 bottles)'),
      (10, 'Divine: Half Case (6 bottles)'),
      (11, 'Host Tasting Kit'),
  )

  product = models.ForeignKey(Product, null=True)
  price_category = models.IntegerField(choices=PRICE_TYPE, default=PRICE_TYPE[0][0])
  quantity = models.IntegerField(default=1)
  frequency = models.IntegerField(choices=SubscriptionInfo.FREQUENCY_CHOICES, default=1)
  total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

  def subtotal(self):
    if self.price_category in [5,7,9]:
      return 2*float(self.product.unit_price)
    elif self.price_category in [6,8,10]:
      return self.product.unit_price
    else:
      return self.quantity*self.product.unit_price

  def quantity_str(self):
    if self.price_category in [5,6,7,8,9,10]:
      return "Full Case" if self.quantity == 1 else "Half Case"
    else:
      return str(self.quantity)

class Cart(models.Model):
  """
    All orders added up
  """
  user = models.ForeignKey(User, null=True)
  items = models.ManyToManyField(LineItem)
  updated = models.DateTimeField(auto_now=True)

  # to track the parties that resulted in orders
  party = models.ForeignKey(Party, null=True)

  CART_STATUS_CHOICES = (
      (0, 'START'),
      (1, 'ADDED ITEM'),
      (2, 'CUSTOMIZE CHECKOUT'),
      (3, 'FILLED SHIPPING'),
      (4, 'FILLED BILLING'),
      (5, 'COMPLETE ORDER'),
  )

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
    shipping = 0
    for item in self.items.all():
      # always $16 - August 2, 2012
      shipping += 16
      """
      if item.price_category in [5, 6, 8]:
        # add shipping for good half, full, better half case
        shipping += 16
      elif item.frequency == 0:
        shipping += 16
      """
    return shipping 

  def tax(self):
    # TODO: tax needs to be calculated based on the state
    tax = float(self.subtotal())*0.06
    return tax 

  def total(self):
    # TODO: total everything including shipping and tax
    return self.shipping() + self.tax() + self.subtotal() 

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
  order_date = models.DateTimeField(auto_now_add=True)

  FULFILL_CHOICES = (
      ( 0, 'Not Ordered' ),
      ( 1, 'Ordered' ),
      ( 2, 'Processing' ),
      ( 3, 'Delayed' ),
      ( 4, 'Out of Stock'),
      ( 5, 'Wine Selected'),
      ( 6, 'Shipped' ),
      ( 7, 'Received' ),
  )
  fulfill_status = models.IntegerField(choices=FULFILL_CHOICES, default=0)

  CARRIER_TYPE = (
      ( 0, 'Unspecified'),
      ( 1, 'FedEx'),
      ( 2, 'UPS' ),
      ( 3, 'DHL' ),
      ( 4, 'USPS' )
  )
  carrier = models.IntegerField(choices=CARRIER_TYPE, default=0)
  tracking_number = models.CharField(max_length=128, null=True, blank=True)
  ship_date = models.DateTimeField(blank=True, null=True)
  last_updated = models.DateTimeField(auto_now=True)

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
    items = self.cart.items.filter(price_category__in=[5,6,7,8,9,10])
    if items.exists():
      return items[0].quantity_str()
    else:
      items = self.cart.items.exclude(price_category__in=[5,6,7,8,9,10])
      if items.exists():
        return items[0].quantity
    return "-"

  def recurring(self):
    items = self.cart.items.filter(frequency__in=[1,2,3])
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
  pro = models.ForeignKey(User)
  party = models.ForeignKey(Party)
  timestamp = models.DateTimeField(auto_now_add=True)

class MySocializer(models.Model):
  """
    Shows the socializers that are assigned to a party pro
  """
  pro = models.ForeignKey(User, related_name="my_socializer")
  socializer = models.ForeignKey(User, related_name="my_pro")
  timestamp = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "%s - %s"%(self.pro, self.socializer)

class CustomizeOrder(models.Model):
  user = models.ForeignKey(User, null=True)

  MIX_CHOICES = (
      ( 0, 'Your Vinely recommendation'),
      ( 1, 'Send me a mix of red & white wine'),
      ( 2, 'Send me red wine only'),
      ( 3, 'Send me white wine only')
  )

  wine_mix = models.IntegerField(choices=MIX_CHOICES, verbose_name="Tell us a little more about what you would like in your shipment.",
                                  default=MIX_CHOICES[0][0])

  SPARKLING_CHOICES = (
      ( 0, 'No thanks' ),
      ( 1, 'Yes' )
  )

  sparkling = models.IntegerField(choices=SPARKLING_CHOICES, verbose_name="Can we include sparkling wine?",
                                    default=SPARKLING_CHOICES[1][0])
  timestamp = models.DateTimeField(auto_now_add=True)

class EngagementInterest(models.Model):
  """
    Interest in becoming party pro or socializers or tasters attending party
  """

  ENGAGEMENT_CHOICES = (
    (1, 'Vinely Pro'),
    (2, 'Vinely Socializer'),
    (3, 'Vinely Taster'),
    (5, 'Tasting Kit'),
  )

  user = models.ForeignKey(User)
  engagement_type = models.IntegerField(choices=ENGAGEMENT_CHOICES, default=ENGAGEMENT_CHOICES[0][0])
  latest = models.DateTimeField(auto_now=True)
  timestamp = models.DateTimeField(auto_now_add=True)

  def update_time(self):
    self.latest = datetime.now()
    self.save()

  def __unicode__(self):
    return "%s interest in %s"%(self.user.email, EngagementInterest.ENGAGEMENT_CHOICES[self.engagement_type][1])

class InvitationSent(models.Model):
  """
    Tracking the invitations sent from Party Details page
  """
  party = models.ForeignKey(Party)
  custom_subject = models.CharField(max_length=128, default="You're invited to a Vinely Party!")
  custom_message = models.CharField(max_length=1024, blank=True, null=True)
  guests = models.ManyToManyField(User)
  timestamp = models.DateTimeField(auto_now_add=True)
