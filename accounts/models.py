from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings
from Crypto.Cipher import AES
import binascii, string
from sorl.thumbnail import ImageField

from personality.models import WinePersonality
from django.contrib.localflavor.us import models as us_models

from datetime import date

# Create your models here.

class Address(models.Model):
  nick_name = models.CharField(max_length=64, null=True, blank=True)
  company_co = models.CharField(max_length=64, null=True, blank=True)
  street1 = models.CharField(verbose_name="Address 1", max_length=128)
  street2 = models.CharField(verbose_name="Address 2", max_length=128, null=True, blank=True)
  city = models.CharField(max_length=64)
  state = us_models.USStateField()
  zipcode = models.CharField(max_length=20, help_text="5 digit or extended zipcode")

  def __unicode__(self):
    return "%s, %s"%(self.street1, self.zipcode)

  def full_text(self):
    return "%s, %s, %s %s"%(self.street1, self.city, self.state, self.zipcode)

  def google_maps_address(self):
    search_str = "%s %s, %s %s"%(self.street1, self.city, self.state, self.zipcode)
    new_str = string.replace(search_str, " ", "+")
    return new_str 

class CreditCard(models.Model):
  nick_name = models.CharField(max_length=64, null=True, blank=True)
  card_number = models.CharField(max_length=32)
  exp_month = models.IntegerField()
  exp_year = models.IntegerField()
  #expiry_date = models.DateField()
  verification_code = models.CharField(max_length=32)
  billing_zipcode = models.CharField(max_length=5, help_text="5 digit zipcode")
  card_type = models.CharField(max_length=10, default="Unknown")

  def last_four(self):
    cipher = AES.new(settings.SECRET_KEY[:32], AES.MODE_ECB)
    card_cipher = binascii.unhexlify(self.card_number)
    pad_number = cipher.decrypt(card_cipher)
    card_num = string.strip(pad_number, 'X')
    return card_num[-4:]

  def exp_date(self):
    return "%s/%s"%(self.exp_month, self.exp_year)

  def encrypt_card_num(self, number):
    """
      saves card number
    """
    pad_number = string.ljust(str(number), 16, 'X')
    cipher = AES.new(settings.SECRET_KEY[:32], AES.MODE_ECB)
    msg = cipher.encrypt(pad_number)
    self.card_number = msg.encode('hex')

  def decrypt_card_num(self, number=None):
    cipher = AES.new(settings.SECRET_KEY[:32], AES.MODE_ECB)
    if number:
      card_cipher = binascii.unhexlify(number)
    else:
      card_cipher = binascii.unhexlify(self.card_number)
    pad_number = cipher.decrypt(card_cipher)
    return string.strip(pad_number, 'X')

  def encrypt_cvv(self, cvv):
    """
      encrypts cvv
    """
    pad_number = string.ljust(str(cvv), 16, 'X')
    cipher = AES.new(settings.SECRET_KEY[:32], AES.MODE_ECB)
    msg = cipher.encrypt(pad_number)
    self.verification_code = msg.encode('hex')

  def decrypt_cvv(self, cvv=None):
    cipher = AES.new(settings.SECRET_KEY[:32], AES.MODE_ECB)
    if cvv:
      card_cipher = binascii.unhexlify(cvv)
    else:
      card_cipher = binascii.unhexlify(self.verification_code)
    pad_number = cipher.decrypt(card_cipher)
    return string.strip(pad_number, 'X')

class VerificationQueue(models.Model):

  VERIFICATION_CHOICES = (
    (0, 'New Account'),
    (1, 'Forgot Password'),
    (2, 'Verify E-mail')
  )

  user = models.ForeignKey(User)
  verification_code = models.CharField(max_length=64)
  verified = models.BooleanField(default=False)
  verification_type = models.IntegerField(choices=VERIFICATION_CHOICES, default=0)
  #: verify_data is used when verifying e-mail only for now
  verify_data = models.CharField(max_length=128, blank=True, null=True)
  created = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
  user = models.OneToOneField(User)

  image = ImageField(upload_to="profiles/", blank=True, null=True)
  dob = models.DateField(verbose_name="Date of Birth", null=True, blank=True)
  # drivers license number
  dl_number = models.CharField(verbose_name="Driver's Licence #", max_length=32, null=True, blank=True)
  phone = us_models.PhoneNumberField(max_length=16, null=True, blank=True)
  accepted_tos = models.BooleanField(verbose_name="I accept the terms of service", default=False)
  news_optin = models.BooleanField(verbose_name="Yes, I'd like to be notified of news, offers and events at Vinely via this email address.", default=True)

  GENDER_CHOICES = (
    (0, 'FEMALE'),
    (1, 'MALE'),
    (2, 'N/A'),
  )

  gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_CHOICES[0][0])
  zipcode = models.CharField(max_length=20, help_text="5 digit or extended zipcode of your primariy residence") 
  above_21 = models.BooleanField(verbose_name="I certify that I am over 21", default=False)
  wine_personality = models.ForeignKey(WinePersonality, null=True, blank=True)
  prequestionnaire = models.BooleanField(default=False)

  # for storing default addresses 
  billing_address = models.ForeignKey(Address, null=True, related_name="billed_to")
  shipping_address = models.ForeignKey(Address, null=True, related_name="shipped_to")
  credit_card = models.ForeignKey(CreditCard, null=True, related_name="owner")

  # for permanently storing for future
  credit_cards = models.ManyToManyField(CreditCard, related_name="owned_by")
  party_addresses = models.ManyToManyField(Address, related_name="hosting_user")
  shipping_addresses = models.ManyToManyField(Address, related_name="shipping_user")

  def age(self):
    year = 365
    age = (date.today() - self.dob).days / year
    return age

def create_user_profile(sender, instance, created, **kwargs):
  if created:
    UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class VinelyProAccount(models.Model):
  """
    Need to create this for every specialist account
    Map wife and husband into one VinelyPro account
  """
  users = models.ManyToManyField(User)
  account_number = models.BigIntegerField()
  comment = models.CharField(max_length=128)

class SubscriptionInfo(models.Model):
  user = models.ForeignKey(User)

  FREQUENCY_CHOICES = (
    (0, 'One-time purchase'),
    (1, 'Monthly'),
    (2, 'Bi-Monthly'),
    (3, 'Quarterly')
  )
  frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=9)

  QUANTITY_CHOICES = (
    (5, 'Good: Full Case (12 bottles)'),
    (6, 'Good: Half Case (6 bottles)'),
    (7, 'Better: Full Case (12 bottles)'),
    (8, 'Better: Half Case (6 bottles)'),
    (9, 'Best: Full Case (12 bottles)'),
    (10, 'Best: Half Case (6 bottles)'),
  )
  quantity = models.IntegerField(choices=QUANTITY_CHOICES, default=0)