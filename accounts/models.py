from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.conf import settings
from Crypto.Cipher import AES
from sorl.thumbnail import ImageField

from personality.models import WinePersonality
from django.contrib.localflavor.us import models as us_models
from django.utils import timezone

from datetime import date, timedelta
import binascii, string, math
from stripecard.models import StripeCard

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
    return "%s, %s" % (self.street1, self.zipcode)

  def full_text(self):
    return "%s, %s, %s %s" % (self.street1, self.city, self.state, self.zipcode)

  def google_maps_address(self):
    search_str = "%s %s, %s %s" % (self.street1, self.city, self.state, self.zipcode)
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
    return "%s/%s" % (self.exp_month, self.exp_year)

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

  vinely_customer_id = models.CharField(max_length=16, blank=True, null=True)

  image = ImageField(upload_to="profiles/", blank=True, null=True)
  dob = models.DateField(verbose_name="Date of Birth", null=True, blank=True)
  # drivers license number
  dl_number = models.CharField(verbose_name="Driver's Licence #", max_length=32, null=True, blank=True)
  phone = us_models.PhoneNumberField(max_length=16, null=True, blank=True)
  work_phone = us_models.PhoneNumberField(max_length=16, null=True, blank=True)
  accepted_tos = models.BooleanField(verbose_name="I accept the terms of service", default=False)
  news_optin = models.BooleanField(verbose_name="Yes, I'd like to be notified of news, offers and events at Vinely via this email address.", default=True)
  mentor = models.ForeignKey(User, default = 1, verbose_name='Vinely Pro Mentor', related_name='mentor')

  GENDER_CHOICES = (
    (0, 'FEMALE'),
    (1, 'MALE'),
    (2, 'N/A'),
  )

  gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_CHOICES[0][0])
  zipcode = models.CharField(max_length=20, help_text="5 digit or extended zipcode of your primariy residence", null=True, blank=True)
  above_21 = models.BooleanField(verbose_name="I certify that I am over 21", default=False)

  wine_personality = models.ForeignKey(WinePersonality, default=7)
  prequestionnaire = models.BooleanField(default=False)

  # for storing default addresses
  billing_address = models.ForeignKey(Address, related_name="billed_to", null=True, blank=True)
  shipping_address = models.ForeignKey(Address, related_name="shipped_to", null=True, blank=True)
  credit_card = models.ForeignKey(CreditCard, related_name="owner", null=True, blank=True)
  stripe_card = models.ForeignKey(StripeCard, related_name="stripe_owner", null=True, blank=True)

  # for permanently storing for future
  credit_cards = models.ManyToManyField(CreditCard, related_name="owned_by", null=True, blank=True)
  stripe_cards = models.ManyToManyField(StripeCard, related_name="stripe_owned_by", null=True, blank=True)
  party_addresses = models.ManyToManyField(Address, related_name="hosting_user", null=True, blank=True)
  shipping_addresses = models.ManyToManyField(Address, related_name="shipping_user", null=True, blank=True)

  def age(self):
    year = 365
    age = (date.today() - self.dob).days / year
    return age

  def is_under_age(self):
    today = timezone.now().date()
    if not self.dob or ((today - self.dob) < timedelta(math.ceil(365.25 * 21))):
      return True
    return False

  def has_personality(self):
    try:
      return self.wine_personality.name != "Mystery"
    except:
      return False

  def role(self):
    pro_group = Group.objects.get(name="Vinely Pro")
    hos_group = Group.objects.get(name="Vinely Host")
    tas_group = Group.objects.get(name="Vinely Taster")

    if pro_group in self.user.groups.all():
      return 'pro'
    if hos_group in self.user.groups.all():
      return 'host'
    if tas_group in self.user.groups.all():
      return 'taster'

  def is_pro(self): return self.role() == 'pro'

  def is_host(self): return self.role() == 'host'

  def is_taster(self): return self.role() == 'taster'

  def personality_rating_code(self):
    # calculate rating code
    from personality.models import WineRatingData

    ratings = WineRatingData.objects.filter(user = self.user).order_by('wine__id')
    r = [x.overall for x in ratings]

    L=[]; D=[]; N=[];
    likes=''; dislikes=''; neutrals='';

    for i,x in enumerate(r):
      if x < 3: D.append(i+1)
      elif x == 3: N.append(i+1)
      elif x > 3: L.append(i+1)

    likes = "L" + "".join(map(str, L)) if len(L) > 0 else ""
    neutrals = "N" + "".join(map(str, N)) if len(N) > 0 else "" 
    dislikes = "D" + "".join(map(str, D)) if len(D) > 0 else ""
    code = likes + neutrals# + dislikes
    return code if code else "-"

  def order_customization_pref(self):
    from main.models import CustomizeOrder
    try:
      pref = CustomizeOrder.objects.get(user=self.user)
      if pref.wine_mix == 1:
        return "Both"
      elif pref.wine_mix == 2:
        return "Red"
      elif pref.wine_mix == 3:
        return "White"
      else:
        return "-"
    except CustomizeOrder.DoesNotExist:
      return "-"

def create_user_profile(sender, instance, created, **kwargs):
  if created:
    UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


class VinelyProAccount(models.Model):
  """
    Need to create this for every Vinely Pro account
    Map wife and husband into one VinelyPro account
  """
  users = models.ManyToManyField(User)
  account_number = models.CharField(max_length = 8)
  comment = models.CharField(max_length=128)


class SubscriptionInfo(models.Model):
  user = models.ForeignKey(User)

  FREQUENCY_CHOICES = (
    (0, 'One-time purchase'),
    (1, 'Monthly'),
    (2, 'Bi-Monthly'),
    (3, 'Quarterly'),
    (9, 'No Subscription'),
  )
  frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=9)

  QUANTITY_CHOICES = (
    (0, 'No Subscription'),
    (5, 'Basic: Full Case (12 bottles)'),
    (6, 'Basic: Half Case (6 bottles)'),
    (7, 'Superior: Full Case (12 bottles)'),
    (8, 'Superior: Half Case (6 bottles)'),
    (9, 'Divine: Full Case (12 bottles)'),
    (10, 'Divine: Half Case (6 bottles)'),
  )
  quantity = models.IntegerField(choices=QUANTITY_CHOICES, default=0)
  next_invoice_date = models.DateField(auto_now_add=True)


class Zipcode(models.Model):
  '''
  List of all zipcodes in US
  '''
  code = models.CharField(max_length = 5)
  country = models.CharField(max_length = 2)
  city = models.CharField(max_length = 32)
  state = models.CharField(max_length = 2)
  latitude = models.CharField(max_length = 20)
  longitude = models.CharField(max_length = 20)

SUPPORTED_STATES = ['MI', 'CA']
