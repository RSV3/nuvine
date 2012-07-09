from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from personality.models import WinePersonality

# Create your models here.

class Address(models.Model):
  nick_name = models.CharField(max_length=64, null=True, blank=True)
  street1 = models.CharField(verbose_name="Street (Line 1)", max_length=128)
  street2 = models.CharField(verbose_name="Street (Line 2)", max_length=128, null=True, blank=True)
  city = models.CharField(max_length=64)
  state = models.CharField(max_length=10)
  zipcode = models.CharField(max_length=20)

class CreditCard(models.Model):
  nick_name = models.CharField(max_length=64)
  card_number = models.CharField(max_length=32)
  exp_month = models.CharField(max_length=2)
  exp_year = models.CharField(max_length=2)
  verification_code = models.CharField(max_length=4)
  billing_zipcode = models.CharField(max_length=5)

class UserProfile(models.Model):
  user = models.OneToOneField(User)

  dob = models.DateField(null=True, blank=True)
  # drivers license number
  dl_number = models.CharField(max_length=32, null=True, blank=True)
  phone = models.CharField(max_length=16, null=True, blank=True)
  accepted_tos = models.BooleanField(default=False)
  age = models.IntegerField(default=0)
  above_21 = models.BooleanField(default=False)
  wine_personality = models.ForeignKey(WinePersonality, null=True, blank=True)

  billing_address = models.ForeignKey(Address, null=True, related_name="billed_to")
  shipping_address = models.ForeignKey(Address, null=True, related_name="shipped_to")
  credit_cards = models.ManyToManyField(CreditCard)

#def create_user_profile(sender, instance, created, **kwargs):
#  if created:
#    UserProfile.objects.create(user=instance)
#
#post_save.connect(create_user_profile, sender=User)