from django.db import models
from django.contrib.auth.models import User

from accounts.models import Address, CreditCard
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
  message = models.TextField()
  zipcode = models.CharField(max_length=12)

class Party(models.Model):

  # default to the name of the host
  host = models.ForeignKey(User)
  title = models.CharField(max_length=128)
  description = models.TextField()
  address = models.ForeignKey(Address)
  phone = models.CharField(max_length=16, verbose_name="Contact phone number", null=True, blank=True)
  created = models.DateTimeField(auto_now_add=True)
  event_date = models.DateTimeField()

  def __unicode__(self):
    return self.title

  def invitees(self):
    invites = PartyInvite.objects.filter(party=self).count()
    coming = PartyInvite.objects.filter(party=self, response__in=[2,3]).count()

    return "%d [%d]"%(invites, coming)

  def num_orders(self):
    # TODO: num orders and num orders pending 
    return "%d [%d]"%(5, 4) 

class PartyInvite(models.Model):

  RESPONSE_CHOICES = (
      (0, 'No Answer'),
      (1, 'No'),
      (2, 'Maybe'),
      (3, 'Yes')
  )

  party = models.ForeignKey(Party)
  invitee = models.ForeignKey(User)
  response = models.IntegerField(choices=RESPONSE_CHOICES, default=RESPONSE_CHOICES[0][0])

class Product(models.Model):
  PRODUCT_TYPE = (
      (0, 'Tasting Kit'),
      (1, 'Wine Package'),
      (2, 'Wine Bottle'),
  )

  name = models.CharField(max_length=128)
  sku = models.CharField(max_length=32, default="xxxxxxxxxxxxxxxxxxxxxxxxxx")
  category = models.IntegerField(choices=PRODUCT_TYPE, default=PRODUCT_TYPE[0][0])
  description = models.CharField(max_length=512)
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
      (5, 'Good: 12 bottles'),
      (6, 'Good: 6 bottles'),
      (7, 'Better: 12 bottles'),
      (8, 'Better: 6 bottles'),
      (9, 'Best: 12 bottles'),
      (10, 'Best: 6 bottles'),
      (11, 'Host Tasting Kit'),
  )

  FREQUENCY_CHOICES = (
      (0, 'One-time purchase'),
      (1, 'Monthly'),
      (2, 'Bi-monthly'),
      (3, 'Quarterly'),
  )

  product = models.ForeignKey(Product, null=True)
  price_category = models.IntegerField(choices=PRICE_TYPE, default=PRICE_TYPE[0][0])
  quantity = models.IntegerField(default=1)
  frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=1)
  total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

  def subtotal(self):
    if self.price_category in [5,7,9]:
      return self.product.unit_price
    elif self.price_category in [6,8,10]:
      return 0.5*float(self.product.unit_price)
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

  def subtotal(self):
    # sum of all line items
    price_sum = 0 
    for o in self.items.all():
      price_sum += float(o.subtotal())
    return price_sum 

  def shipping(self):
    # TODO: flat rate
    return 16 

  def tax(self):
    # TODO: tax needs to be calculated based on the state
    return 22

  def total(self):
    # TODO: total everything including shipping and tax
    return 1525

class Order(models.Model):
  """
    An order is created when a user finally pays for the order

    The orders also indicate how frequently it will be fulfilled
  """
  user = models.ForeignKey(User)
  # unique order id
  order_id = models.CharField(max_length=128) 
  cart = models.OneToOneField(Cart)
  shipping_address = models.ForeignKey(Address, null=True)
  credit_card = models.ForeignKey(CreditCard, null=True)
  order_date = models.DateTimeField(auto_now_add=True)

  FULFILL_CHOICES = (
      ( 0, 'Ordered' ),
      ( 1, 'Processing' ),
      ( 2, 'Delayed' ),
      ( 3, 'Out of Stock'),
      ( 4, 'Shipped' ),
      ( 5, 'Received' ),
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

class OrderFulfilled(models.Model):
  """
    Every time an order is fulfilled it is logged here
  """
  order = models.ForeignKey(Order)
  fulfilled_date = models.DateTimeField(auto_now_add=True)

class OrderReview(models.Model):
  """
    One order review per wine
    Multiple order review per order
  """
  user = models.ForeignKey(User)
  order = models.ForeignKey(Order)
  wine_rating = models.ForeignKey(WineRatingData)
  timestamp = models.DateTimeField(auto_now_add=True)

class MyHosts(models.Model):
  """
    Shows the hosts that are assigned to a party specialist
  """
  specialist = models.ForeignKey(User, related_name="my_hosts")
  host = models.ForeignKey(User, related_name="my_specialist")
  timestamp = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "%s - %s"%(specialist, host)

class CustomizeOrder(models.Model):
  user = models.ForeignKey(User, null=True)

  MIX_CHOICES = (
      ( 0, 'Send me a mix of red & white wine'),
      ( 1, 'Send me red wine only'),
      ( 2, 'Send me white wine only')
  )

  wine_mix = models.IntegerField(choices=MIX_CHOICES, verbose_name="Tell us a little more about what you would like in your shipment.")

  SPARKLING_CHOICES = (
      ( 0, 'No' ),
      ( 1, 'Yes' )
  )

  sparkling = models.IntegerField(choices=SPARKLING_CHOICES, verbose_name="Can we include sparkling wine?")
  timestamp = models.DateTimeField(auto_now_add=True)
