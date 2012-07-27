from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from personality.models import WinePersonality
from django.contrib.localflavor.us import models as us_models


# Create your models here.

class Address(models.Model):
  nick_name = models.CharField(max_length=64, null=True, blank=True)
  company_co = models.CharField(max_length=64, null=True, blank=True)
  street1 = models.CharField(verbose_name="Address 1", max_length=128)
  street2 = models.CharField(verbose_name="Address 2", max_length=128, null=True, blank=True)
  city = models.CharField(max_length=64)
  state = us_models.USStateField()
  zipcode = models.CharField(max_length=20)

  def __unicode__(self):
    return "%s, %s"%(self.street1, self.zipcode)

  def full_text(self):
    return "%s, %s, %s %s"%(self.street1, self.city, self.state, self.zipcode)

class CreditCard(models.Model):
  nick_name = models.CharField(max_length=64, null=True, blank=True)
  card_number = models.CharField(max_length=32)
  exp_month = models.IntegerField()
  exp_year = models.IntegerField()
  #expiry_date = models.DateField()
  verification_code = models.CharField(max_length=4)
  billing_zipcode = models.CharField(max_length=5, help_text="5 digit zipcode")

  def last_four(self):
    return self.card_number[-4:]

  def exp_date(self):
    return "%s/%s"%(self.exp_month, self.exp_year)

class VerificationQueue(models.Model):
  user = models.ForeignKey(User)
  verification_code = models.CharField(max_length=64)
  verified = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
  user = models.OneToOneField(User)

  dob = models.DateField(verbose_name="Date of Birth", null=True, blank=True)
  # drivers license number
  dl_number = models.CharField(verbose_name="Driver's Licence #", max_length=32, null=True, blank=True)
  phone = us_models.PhoneNumberField(max_length=16, null=True, blank=True)
  accepted_tos = models.BooleanField(verbose_name="I accept the terms of service", default=False)
  news_optin = models.BooleanField(verbose_name="Yes, I'd like to be notified of news, offers and events at Vinely via this email address.", default=False)
  age = models.IntegerField(default=0)
  above_21 = models.BooleanField(verbose_name="I certify that I am over 21", default=False)
  wine_personality = models.ForeignKey(WinePersonality, null=True, blank=True)

  billing_address = models.ForeignKey(Address, null=True, related_name="billed_to")
  shipping_address = models.ForeignKey(Address, null=True, related_name="shipped_to")

  credit_cards = models.ManyToManyField(CreditCard)
  party_addresses = models.ManyToManyField(Address, related_name="hosting_user")
  shipping_addresses = models.ManyToManyField(Address, related_name="shipping_user")

def create_user_profile(sender, instance, created, **kwargs):
  if created:
    UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

