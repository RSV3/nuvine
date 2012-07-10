from django.db import models
from django.contrib.auth.models import User

from accounts.models import Address
from personality.models import WineRatingData

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
  name = models.CharField(max_length=128)
  description = models.TextField()
  address = models.ForeignKey(Address)
  phone = models.CharField(max_length=16, verbose_name="Contact phone number", null=True, blank=True)
  created = models.DateTimeField(auto_now_add=True)
  event_date = models.DateTimeField()

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

class LineItem(models.Model):

  PRICE_TYPE = (
      (0, 'Product'),
      (1, 'Service'),
      (2, 'Sales Tax'),
      (3, 'Shipping'),
      (4, 'Discount'),
      (5, 'Good: 6 bottles'),
      (6, 'Good: 12 bottles'),
      (7, 'Better: 6 bottles'),
      (8, 'Better: 12 bottles'),
      (9, 'Best: 6 bottles'),
      (10, 'Best: 12 bottles'),
  )

  name = models.CharField(max_length=64)
  quantity = models.IntegerField(default=0)
  price_category = models.IntegerField(choices=PRICE_TYPE, default=PRICE_TYPE)
  unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
  total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class Cart(models.Model):
  """
    All orders added up
  """
  user = models.ForeignKey(User)
  orders = models.ManyToManyField(LineItem)
  updated = models.DateTimeField(auto_now=True)

class Order(models.Model):
  """
    An order is created when a user finally pays for the order
  """
  FREQUENCY_CHOICES = (
      (0, 'Monthly'),
      (1, 'Bi-monthly'),
      (2, 'Quarterly'),
      (3, 'One-time purchase')
  )

  user = models.ForeignKey(User)
  # unique order id
  order_id = models.CharField(max_length=128) 
  cart = models.OneToOneField(Cart)
  frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=0)
  order_date = models.DateTimeField(auto_now_add=True)
  fulfilled = models.BooleanField(default=False)
  fulfilled_date = models.DateTimeField()

  def fulfill_order(self):
    self.fulfilled = True
    self.fulfilled_date = datetime.today()
    self.save()

class OrderReview(models.Model):
  """
    One order review per wine
    Multiple order review per order
  """
  user = models.ForeignKey(User)
  order = models.ForeignKey(Order)
  wine_rating = models.ForeignKey(WineRatingData)
  timestamp = models.DateTimeField(auto_now_add=True)

