from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.conf import settings
from Crypto.Cipher import AES
from sorl.thumbnail import ImageField

from personality.models import WinePersonality
from django.contrib.localflavor.us import models as us_models
from django.utils import timezone

from datetime import datetime, date, timedelta, tzinfo
import binascii, string, math
from stripecard.models import StripeCard

from personality.models import WineRatingData

from dateutil.relativedelta import relativedelta
from django.http import HttpRequest

import stripe
ZERO = timedelta(0)

import logging

log = logging.getLogger(__name__)


# Create your models here.

# have to redefine instead of importing from main.utils due to circular dependency
class UTC(tzinfo):
  """UTC"""

  def utcoffset(self, dt):
    return ZERO

  def tzname(self, dt):
    return "UTC"

  def dst(self, dt):
    return ZERO


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
  card_type = models.CharField(max_length=32, default="Unknown")

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
  mentor = models.ForeignKey(User, default=1, verbose_name='Vinely Pro Mentor', related_name='mentor')

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

  def update_stripe_subscription(self, frequency, quantity):
    current_shipping = self.shipping_address
    user_state = Zipcode.objects.get(code=current_shipping.zipcode).state
    stripe_card = self.stripe_card

    if user_state in Cart.STRIPE_STATES:
      if user_state == 'MI':
        stripe.api_key = settings.STRIPE_SECRET
      elif user_state == 'CA':
        stripe.api_key = settings.STRIPE_SECRET_CA

      if stripe_card:
        customer = stripe.Customer.retrieve(id=stripe_card.stripe_user)
        #print 'customer.subscription', customer.subscription
        if frequency == 1 and quantity != 0:
          # for now only have monthly subscription
          stripe_plan = SubscriptionInfo.STRIPE_PLAN[frequency][quantity - 5]
          customer.update_subscription(plan=stripe_plan)
        else:
          if customer.subscription:
            # in order to keep track of subscription history, we add new entry with no subscription
            subscription = SubscriptionInfo(user=self.user, frequency=9, quantity=0, next_invoice_date=datetime.now(tz=UTC()))
            subscription.save()
            customer.cancel_subscription()
        return True

      # there's no stripe subscription that can be updated
      return False

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

  def is_pro(self):
    return self.role() == 'pro'

  def is_host(self):
    return self.role() == 'host'

  def is_taster(self):
    return self.role() == 'taster'

  def cancel_subscription(self):
    """
      Cancels user subscription
    """
    # in order to keep track of subscription history, we add new entry with no subscription
    subscription = SubscriptionInfo(user=self.user, frequency=9, quantity=0, next_invoice_date=datetime.now(tz=UTC()))
    subscription.save()

    # need to cancel credit card charges (i.e. Stripe)
    if self.stripe_card:
      customer = stripe.Customer.retrieve(id=self.stripe_card.stripe_user)
      customer.cancel_subscription()

  def personality_rating_code(self):
    html = '''
    <center>
    <table class='table table-striped'>
      <thead>
        <tr>
          <th>Wine</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        %s
      </tbody>
    </table>
    </center>
    '''
    # calculate rating code
    ratings = WineRatingData.objects.filter(user=self.user).order_by('wine__number')
    r = [x.overall for x in ratings]

    L = []; D = []; N = [];
    likes = ''; dislikes = ''; neutrals = '';
    rows = ''
    for i, x in enumerate(r):
      if x < 3:
        D.append(i + 1)
        rows += "<tr><td>%s</td><td>%s</td></tr>" % (i + 1, "-")
      elif x == 3:
        N.append(i + 1)
        rows += "<tr><td>%s</td><td>%s</td></tr>" % (i + 1, "Neutral")
      elif x > 3:
        L.append(i + 1)
        rows += "<tr><td>%s</td><td>%s</td></tr>" % (i + 1, "Likes")

    html = html % rows
    likes = "L" + "".join(map(str, L)) if len(L) > 0 else ""
    neutrals = "N" + "".join(map(str, N)) if len(N) > 0 else ""
    dislikes = "D" + "".join(map(str, D)) if len(D) > 0 else ""
    code = likes + neutrals  # + dislikes
    code = code if code else "-"
    return (code, html)

  def order_customization_pref(self):
    from main.models import CustomizeOrder
    try:
      pref = CustomizeOrder.objects.get(user=self.user)
      if pref.wine_mix == 0:  # Vinely recommendation
        whites = [1, 2, 3]
        reds = [4, 5, 6]

        # use the wine ratings
        likes_reds = WineRatingData.objects.filter(user=self.user, wine__number__in=reds, overall__gt=3).exists()
        likes_whites = WineRatingData.objects.filter(user=self.user, wine__number__in=whites, overall__gt=3).exists()
        if likes_reds and likes_whites:
          return "Both"
        elif likes_reds:
          return "Red"
        elif likes_whites:
          return "White"
        else:
          neutral_whites = WineRatingData.objects.filter(user=self.user, wine__number__in=whites, overall=3).exists()
          neutral_reds = WineRatingData.objects.filter(user=self.user, wine__number__in=whites, overall=3).exists()
          if neutral_reds and neutral_whites:
            return "Both"
          elif neutral_whites:
            return "White"
          elif neutral_reds:
            return "Red"
          else:
            return "-"
      elif pref.wine_mix == 1:
        return "Both"
      elif pref.wine_mix == 2:
        return "Red"
      elif pref.wine_mix == 3:
        return "White"
      else:
        return "-"
    except CustomizeOrder.DoesNotExist:
      return "-"

  def find_neutral_wines(self):
    neutrals = WineRatingData.objects.filter(user=self.user, overall__gte=3).values_list('wine__number', flat=True)
    if len(neutrals) > 0:
      return neutrals
    else:
      # all wines can be used since no rating
      return [1, 2, 3, 4, 5, 6]

  def find_like_wines(self):
    likes = WineRatingData.objects.filter(user=self.user, overall__gte=4).values_list('wine__number', flat=True)
    if len(likes) > 0:
      return likes
    else:
      # all wines can be used since no rating
      return [1, 2, 3, 4, 5, 6]


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
  account_number = models.CharField(max_length=8)
  comment = models.CharField(max_length=128)


class SubscriptionInfo(models.Model):
  user = models.ForeignKey(User)

  # matrix of frequency x quantity
  STRIPE_PLAN = (
    ('', ),  # one time purchase
    ('full-case-basic-monthly', 'half-case-basic-monthly', 'full-case-superior-monthly', 'half-case-superior-monthly', 'full-case-divine-monthly', 'half-case-divine-monthly', '', '3-bottles', '6-bottles', '12-bottles'),  # monthly
    ('full-case-basic-bimonthly', 'half-case-basic-bimonthly', 'full-case-superior-bimonthly', 'half-case-superior-bimonthly', 'full-case-divine-bimonthly', 'half-case-divine-bimonthly'),  # bimonthly
    ('full-case-basic-quarterly', 'half-case-basic-quarterly', 'full-case-superior-quarterly', 'half-case-superior-quarterly', 'full-case-divine-quarterly', 'half-case-divine-quarterly'),  # quarterly
  )

  FREQUENCY_CHOICES = (
    (0, 'One-time purchase'),
    (1, 'Monthly'),
    # (2, 'Bi-Monthly'),
    # (3, 'Quarterly'),
    (9, 'No Subscription'),
  )
  frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=9)

  # Make sure these map to LineItem.PRICE_TYPE
  QUANTITY_CHOICES = (
    (0, 'No Subscription'),
    (5, 'Basic: Full Case (12 bottles)'),
    (6, 'Basic: Half Case (6 bottles)'),
    (7, 'Superior: Full Case (12 bottles)'),
    (8, 'Superior: Half Case (6 bottles)'),
    (9, 'Divine: Full Case (12 bottles)'),
    (10, 'Divine: Half Case (6 bottles)'),
    (12, '3 Bottles'),
    (13, '6 Bottles'),
    (14, '12 Bottles'),
  )
  quantity = models.IntegerField(choices=QUANTITY_CHOICES, default=0)
  next_invoice_date = models.DateField(null=True, blank=True)
  updated_datetime = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return "%s, %s" % (self.get_quantity_display(), self.get_frequency_display())

  def update_subscription_order(self, charge_stripe=True):
    from main.models import Cart, Order, Product, PartyInvite, LineItem
    from main.utils import send_order_confirmation_email

    user = self.user

    prof = user.get_profile()
    shipping_address = prof.shipping_address

    # determine if need to use stripe or native processing
    receiver_state = shipping_address.state

    if (receiver_state in Cart.STRIPE_STATES) and charge_stripe:
      if receiver_state == 'MI':
        stripe.api_key = settings.STRIPE_SECRET
      elif receiver_state == 'CA':
        stripe.api_key = settings.STRIPE_SECRET_CA
      credit_card = prof.credit_card

      if settings.DEPLOY:
        card_number = credit_card.decrypt_card_num()
        cvc = credit_card.decrypt_cvv()
      else:
        cvc = '111'
        if credit_card.card_type == 'American Express':
          card_number = '378282246310005'
        elif credit_card.card_type == 'Master Card':
          card_number = '5105105105105100'
        else:
          card_number = '4242424242424242'

      card = {'number': card_number, 'exp_month': credit_card.exp_month, 'exp_year': credit_card.exp_year,
              'name': '%s %s' % (user.first_name, user.last_name), 'address_zip': credit_card.billing_zipcode,
              }

      # some cards dont have a verification code so only include cvc for those that have
      if cvc:
        card['cvc'] = cvc

      # no record of this customer-card mapping so create
      try:
        customer = stripe.Customer.create(card=card, email=user.email)
        # up profile
        stripe_card = StripeCard.objects.create(stripe_user=customer.id, exp_month=customer.active_card.exp_month,
                            exp_year=customer.active_card.exp_year, last_four=customer.active_card.last4,
                            card_type=customer.active_card.type, billing_zipcode=credit_card.billing_zipcode)

        prof.stripe_card = stripe_card
        prof.save()
        prof.stripe_cards.add(stripe_card)
        log.info('Created stripe profile for %s %s <%s>' % (user.first_name, user.last_name, user.email))
      except Exception, e:
        # TODO: send email to care/support if card is declined
        log.error("Error creating stripe card %s" % e)
        log.error('Card was declined by stripe for %s %s <%s>' % (user.first_name, user.last_name, user.email))
        return

    product = None
    if self.quantity in [5, 7, 9]:
      # full case
      quantity_code = 1
      if self.quantity == 5:
        # product = Product.objects.get(id=4)
        product = Product.objects.get(cart_tag='basic')
      elif self.quantity == 7:
        # product = Product.objects.get(id=5)
        product = Product.objects.get(cart_tag='divine')
      elif self.quantity == 9:
        # product = Product.objects.get(id=6)
        product = Product.objects.get(cart_tag='superior')
    elif self.quantity in [6, 8, 10]:
      # half case
      quantity_code = 2
      if self.quantity == 6:
        # product = Product.objects.get(id=4)
        product = Product.objects.get(cart_tag='basic')
      elif self.quantity == 8:
        # product = Product.objects.get(id=5)
        product = Product.objects.get(cart_tag='divine')
      elif self.quantity == 10:
        # product = Product.objects.get(id=6)
        product = Product.objects.get(cart_tag='superior')
    elif self.quantity in [12, 13, 14]:
      quantity_code = 3
      if self.quantity == 12:
        product = Product.objects.get(cart_tag='3')
      elif self.quantity == 13:
        product = Product.objects.get(cart_tag='6')
      elif self.quantity == 14:
        product = Product.objects.get(cart_tag='12')

    if product is None:
      log.info("%s %s <%s> does not have a subscription product" % (user.first_name, user.last_name, user.email))

    item = LineItem(product=product, price_category=self.quantity, quantity=quantity_code, frequency=self.frequency)
    item.save()

    # party should be same as from last order or first party they participated in
    first_invite = None
    invites = PartyInvite.objects.filter(invitee=user).order_by('party__event_date')
    if invites.exists():
      first_invite = invites[0]
      log.info("First party date: %s" % first_invite.party.event_date)
    else:
      log.info("No first party for: %s " % user.email)

    # find party from last order
    last_order = None
    all_orders = Order.objects.filter(receiver=user).order_by('-order_date')
    if all_orders.exists():
      last_order = all_orders[0]

    cart = Cart(user=user, receiver=user, adds=1)
    if last_order and last_order.cart.party:
      cart.party = last_order.cart.party
    elif first_invite:
      cart.party = first_invite.party
    else:
      # there's no party to associate to
      log.info("There's no party for: %s" % user.email)
    cart.save()
    cart.items.add(item)
    cart.discount = cart.calculate_discount()
    cart.save()

    order = Order(ordered_by=user, receiver=user, cart=cart,
          shipping_address=shipping_address, order_date=timezone.now())

    if prof.stripe_card:
      order.stripe_card = prof.stripe_card
    else:
      order.credit_card = prof.credit_card

    order.assign_new_order_id()
    order.save()
    log.info("Created a new order for %s %s <%s>" % (user.first_name, user.last_name, user.email))

    if receiver_state in Cart.STRIPE_STATES:
      if cart.discount > 0:
        # customer = stripe.Customer.retrieve(id=customer.id)
        coupon = stripe.Coupon.create(amount_off=int(cart.discount * 100), duration='once', currency='usd')
        customer.coupon = coupon.id
        customer.save()

    if (receiver_state in Cart.STRIPE_STATES) and charge_stripe:
      try:

        stripe.InvoiceItem.create(customer=customer.id, amount=int(order.cart.tax() * 100), currency='usd', description='Tax')
        stripe_plan = SubscriptionInfo.STRIPE_PLAN[item.frequency][item.price_category - 5]
        customer.update_subscription(plan=stripe_plan)
        log.info("Subscription updated on stripe for: %s %s <%s>" % (user.first_name, user.last_name, user.email))
      except Exception, e:
        # TODO: send email to care/support if card is declined
        log.error("Error processing subscription on stripe %s" % e)
        log.error('Could not create subscruption on stripe for %s %s <%s>' % (user.first_name, user.last_name, user.email))

    # need to update next invoice date on subscription
    if self.frequency == 1:
      next_invoice = datetime.date(datetime.now(tz=UTC())) + relativedelta(months=+1)
    elif self.frequency == 2:
      next_invoice = datetime.date(datetime.now(tz=UTC())) + relativedelta(months=+2)
    elif self.frequency == 3:
      next_invoice = datetime.date(datetime.now(tz=UTC())) + relativedelta(months=+3)
    self.next_invoice_date = next_invoice
    self.save()

    # send out verification e-mail, create a verification code
    request = HttpRequest()
    request.META['SERVER_NAME'] = "www.vinely.com"
    request.META['SERVER_PORT'] = 80
    request.user = user
    request.session = {}

    send_order_confirmation_email(request, order.order_id)


class Zipcode(models.Model):
  '''
  List of all zipcodes in US
  '''
  code = models.CharField(max_length=5)
  country = models.CharField(max_length=2)
  city = models.CharField(max_length=32)
  state = models.CharField(max_length=2)
  latitude = models.CharField(max_length=20)
  longitude = models.CharField(max_length=20)

SUPPORTED_STATES = ['MI', 'CA', 'MA']
