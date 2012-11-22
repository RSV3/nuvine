from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.http import HttpRequest

from optparse import make_option
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from accounts.models import CreditCard, Address, VerificationQueue
from main.models import SubscriptionInfo, CustomizeOrder, Party, LineItem, Cart, Product, Order
from main.utils import UTC, send_order_added_email, send_to_supplier_order_added_email
from personality.models import WinePersonality, Wine, WineRatingData
from creditcard.utils import get_cc_type
from emailusernames.utils import create_user

from lepl.apps.rfc3696 import Email
import uuid

import xlrd

ORDER_ID = 0
CUSTOMER_ID = 1
RECIPIENT_FIRST_NAME = 2
RECIPIENT_LAST_NAME = 3
RECIPIENT_COMPANY = 4
RECIPIENT_ADDRESS_1 = 5
RECIPIENT_ADDRESS_2 = 6
RECIPIENT_CITY = 7
RECIPIENT_STATE = 8
RECIPIENT_ZIPCODE = 9
RECIPIENT_COUNTRY = 10
RECIPIENT_HOME_PHONE = 11
RECIPIENT_WORK_PHONE = 12
RECIPIENT_EMAIL = 13
CUSTOMER_FIRST_NAME = 14
CUSTOMER_LAST_NAME = 15
CUSTOMER_ADDRESS = 16
CUSTOMER_CITY = 17
CUSTOMER_STATE = 18
CUSTOMER_ZIPCODE = 19
CUSTOMER_EMAIL = 20
CREDIT_CARD_TYPE = 21
CREDIT_CARD_NUM = 22
CREDIT_CARD_CVV = 23
CREDIT_CARD_EXP = 24
BILLING_ZIPCODE = 25
SPECIAL_INSTRUCTIONS = 26
GIFT_MESSAGE = 27
INSURANCE_AMOUNT = 28
ORDER_RETAIL_AMOUNT = 29
TAX_CHARGED = 30
SHIPPING_CHARGED = 31

PROD1_SKU = 32
PROD1_QUANTITY = 33
PROD1_NAME = 34
PROD1_TAX = 35
PROD1_PRICE = 36

PROD2_SKU = 37
PROD2_QUANTITY = 38
PROD2_NAME = 39
PROD2_TAX = 40
PROD2_PRICE = 41

PROD3_SKU = 42
PROD3_QUANTITY = 43
PROD3_NAME = 44
PROD3_TAX = 45
PROD3_PRICE = 46

PROD4_SKU = 47
PROD4_QUANTITY = 48
PROD4_NAME = 49
PROD4_TAX = 50
PROD4_PRICE = 51

PROD5_SKU = 52
PROD5_QUANTITY = 53
PROD5_NAME = 54
PROD5_TAX = 55
PROD5_PRICE = 56

PROD6_SKU = 57
PROD6_QUANTITY = 58
PROD6_NAME = 59
PROD6_TAX = 60
PROD6_PRICE = 61

PROD7_SKU = 62
PROD7_QUANTITY = 63
PROD7_NAME = 64
PROD7_TAX = 65
PROD7_PRICE = 66

PROD8_SKU = 67
PROD8_QUANTITY = 68
PROD8_NAME = 69
PROD8_TAX = 70
PROD8_PRICE = 71

PROD9_SKU = 72
PROD9_QUANTITY = 73
PROD9_NAME = 74
PROD9_TAX = 75
PROD9_PRICE = 76

PROD10_SKU = 77
PROD10_QUANTITY = 78
PROD10_NAME = 79
PROD10_TAX = 80
PROD10_PRICE = 81

PROD11_SKU = 82
PROD11_QUANTITY = 83
PROD11_NAME = 84
PROD11_TAX = 85
PROD11_PRICE = 86

PROD12_SKU = 87
PROD12_QUANTITY = 88
PROD12_NAME = 89
PROD12_TAX = 90
PROD12_PRICE = 91

DATE_SHIPPED = 92
TRACKING_NUMBER = 93

SUBSCRIPTION_FREQ = 94
PRICE_TIER = 95
QUANTITY = 96
RED_WHITE = 97
SPARKLING = 98
CREDIT_OUTSTANDING = 99
WINE_PERSONALITY = 100

FULFILLMENT_TYPE_A = 101
FULFILLMENT_TYPE_B = 102


def get_subscription_frequency(subscription_str):
  if subscription_str.strip().lower() in ["one time", 'once']:
    return 0, False
  elif subscription_str.strip().lower() in ["monthly"]:
    return 1, False
  elif subscription_str.strip().lower() in ["bi-monthly"]:
    return 2, False
  elif subscription_str.strip().lower() in ["quarterly"]:
    return 3, False
  elif subscription_str.strip().lower() in ["monthly-susp"]:
    return 1, True

def get_subscription_quantity(price_tier, quantity_float, rownum=0):
  """
    rownum when imported from Excel file
  """

  cart_tag = price_tier.strip().lower()
  if cart_tag in ['taste', 'kit']:
    product = Product.objects.get(pk=1)
  else:
    product = Product.objects.get(cart_tag=price_tier.strip().lower())
  quantity = int(quantity_float)
  if quantity == 6:
    quantity_code = 0
    # 6, 8, 10
    if product.id == 4:
      price_category = 6
      # ^ basic
    elif product.id == 5:
      price_category = 8
      # ^ superior
    elif product.id == 6:
      price_category = 10
      # ^ divine
    else:
      price_category = 11
      # ^ tasting kit
  elif quantity == 12:
    quantity_code = 1
    # 5, 7, 9
    if product.id == 4:
      price_category = 5
      # ^ basic
    elif product.id == 5:
      price_category = 7
      # ^ superior
    elif product.id == 6:
      price_category = 9
      # ^ divine
    else:
      price_category = 11
      # ^ tasting kit
  else:
    print "Invalid quantity of wine bottles for row %d" % rownum
    product = None
    price_category = 0
    quantity_code = 0
  return product, price_category, quantity_code


class Command(BaseCommand):

  args = ''
  help = 'Read orders that have not been recorded'

  option_list = BaseCommand.option_list + (
    make_option('-f', '--file',
            type='string',
            dest='filename',
            default=None,
            help='The excel file name of master database.'),
    )

  def handle(self, *args, **options):
    # Read excel file, go through each column

    taster_group = Group.objects.get(name="Vinely Taster")
    email_validator = Email()
    customer_temp_password = None
    customer_verification_code = None
    receiver_temp_password = None
    receiver_verification_code = None

    if options['filename']:
      wb = xlrd.open_workbook(options['file'])
    else:
      wb = xlrd.open_workbook("data/orders_ingest_11142012.xlsx")

    sheet = wb.sheet_by_name("Orders")

    for rownum in range(1, sheet.nrows):
      row = sheet.row_values(rownum)
      # find user first

      customer_email = row[CUSTOMER_EMAIL].strip().lower()
      recipient_email = row[RECIPIENT_EMAIL].strip().lower()
      print "%s Processing row: %d, %s\tSend to: %s" % (customer_email==recipient_email, rownum, customer_email, recipient_email )
      # check if valid e-mail exists
      if not email_validator(customer_email):
        # go to next line
        continue

      try:
        u = User.objects.get(email=customer_email)
        if not u.first_name:
          u.first_name = row[CUSTOMER_FIRST_NAME]
          u.last_name = row[CUSTOMER_LAST_NAME]
      except User.DoesNotExist:
        print "New user created for customer", rownum, customer_email
        u = create_user(row[CUSTOMER_EMAIL], 'welcome')
        u.first_name = row[CUSTOMER_FIRST_NAME].strip()
        u.last_name = row[CUSTOMER_LAST_NAME].strip()
        u.is_active = False
        customer_temp_password = User.objects.make_random_password()
        u.set_password(customer_temp_password)
        u.save()
        u.groups.add(taster_group)
        u.save()

        customer_verification_code = str(uuid.uuid4())
        vque = VerificationQueue(user=u, verification_code=customer_verification_code)
        vque.save()

      customer_full_name = "%s %s" % (u.first_name, u.last_name)

      # create receiver user
      if u.email == recipient_email:
        receiver = u
      else:
        # check to see if receiver already has account
        try:
          receiver = User.objects.get(email=recipient_email)
          if not receiver.first_name:
            receiver.first_name = row[CUSTOMER_FIRST_NAME]
            receiver.last_name = row[CUSTOMER_LAST_NAME]
        except User.DoesNotExist:
          print "New user created for receiver", rownum, recipient_email
          receiver = create_user(row[RECIPIENT_EMAIL], 'welcome')
          receiver.first_name = row[RECIPIENT_FIRST_NAME].strip()
          receiver.last_name = row[RECIPIENT_LAST_NAME].strip()
          receiver.is_active = False
          receiver.save()
          receiver.groups.add(taster_group)
          receiver_temp_password = User.objects.make_random_password()
          receiver.set_password(receiver_temp_password)
          receiver.save()
          receiver.groups.add(taster_group)
          receiver.save()

          receiver_verification_code = str(uuid.uuid4())
          vque = VerificationQueue(user=receiver, verification_code=receiver_verification_code)
          vque.save()

      receiver_full_name = "%s %s" % (receiver.first_name, receiver.last_name)

      # create item
      product, price_category, quantity_code = get_subscription_quantity(row[PRICE_TIER], row[QUANTITY])
      if product is None:
        print "No valid product found"
        continue

      order_frequency, suspended = get_subscription_frequency(row[SUBSCRIPTION_FREQ])
      item = LineItem(product=product, price_category=price_category, quantity=quantity_code, frequency=order_frequency)
      item.save()

      cart = Cart(user=u, adds=1)
      cart.save()
      cart.items.add(item)
      cart.save()

      customize, created = CustomizeOrder.objects.get_or_create(user=receiver)
      wine_mix_choice = row[RED_WHITE].strip().lower()
      if not wine_mix_choice or wine_mix_choice == "vinely":
        customize.wine_mix = 0
      elif wine_mix_choice == "both":
        customize.wine_mix = 1
      elif wine_mix_choice == "red":
        customize.wine_mix = 2
      elif wine_mix_choice == "white":
        customize.wine_mix = 3
      sparkling_choice = row[SPARKLING].strip().lower()
      customize.sparkling = 0 if sparkling_choice in ["no"] else 1
      customize.save()

      # save customization for customer who ordered if different
      if u != receiver:
        customize, created = CustomizeOrder.objects.get_or_create(user=u)
        wine_mix_choice = row[RED_WHITE].strip().lower()
        if not wine_mix_choice or wine_mix_choice == "vinely":
          customize.wine_mix = 0
        elif wine_mix_choice == "both":
          customize.wine_mix = 1
        elif wine_mix_choice == "red":
          customize.wine_mix = 2
        elif wine_mix_choice == "white":
          customize.wine_mix = 3
        sparkling_choice = row[SPARKLING].strip().lower()
        customize.sparkling = 0 if sparkling_choice in ["no"] else 1
        customize.save()

      # create shipping address
      company_co = row[RECIPIENT_COMPANY]
      if not company_co and customer_full_name != receiver_full_name:
        company_co = receiver_full_name
      recipient_zip = row[RECIPIENT_ZIPCODE] if row[RECIPIENT_ZIPCODE] else 0
      customer_zip = row[CUSTOMER_ZIPCODE] if row[CUSTOMER_ZIPCODE] else 0
      if u.email == receiver.email and u.first_name != row[RECIPIENT_FIRST_NAME].strip():
        # need to use the c/o
        shipping_address = Address(nick_name=receiver_full_name, company_co=company_co,
                          street1=row[RECIPIENT_ADDRESS_1], street2=row[RECIPIENT_ADDRESS_2],
                          city=row[RECIPIENT_CITY], state=row[RECIPIENT_STATE], zipcode=str(int(recipient_zip)).zfill(5))

      else:
        # use customer's address
        shipping_address = Address(nick_name=customer_full_name, company_co=company_co,
                          street1=row[RECIPIENT_ADDRESS_1], street2=row[RECIPIENT_ADDRESS_2],
                          city=row[RECIPIENT_CITY], state=row[RECIPIENT_STATE], zipcode=str(int(recipient_zip)).zfill(5))

      shipping_address.save()

      billing_address = Address(nick_name=customer_full_name,
                                street1=row[CUSTOMER_ADDRESS], city=row[CUSTOMER_CITY],
                                state=row[CUSTOMER_STATE], zipcode=str(int(customer_zip)).zfill(5))
      billing_address.save()

      # create credit card
      billing_zipcode = row[BILLING_ZIPCODE] if row[BILLING_ZIPCODE] else 0
      if not billing_zipcode:
        billing_zipcode = customer_zip

      card_num = row[CREDIT_CARD_NUM].strip()
      card = None
      if card_num:
        cvv_num = row[CREDIT_CARD_CVV].strip()
        card_type = get_cc_type(row[CREDIT_CARD_NUM])

        exp_date = datetime.strptime(row[CREDIT_CARD_EXP].strip(), "%m/%y")
        card = CreditCard(nick_name=customer_email, card_number=card_num,
                    exp_month=exp_date.month, exp_year=exp_date.year, verification_code=cvv_num,
                    billing_zipcode=str(int(billing_zipcode)).zfill(5),
                    card_type=card_type)
        card.save()
        # encrypt card number
        card.encrypt_card_num(card_num)
        card.encrypt_cvv(cvv_num)
        card.save()

      phone_num = row[RECIPIENT_HOME_PHONE].strip().lower()

      # add shipping address to user account
      user_profile = u.get_profile()
      user_profile.shipping_address = shipping_address
      user_profile.shipping_addresses.add(shipping_address)
      if card:
        user_profile.credit_card = card
        user_profile.credit_cards.add(card)
      user_profile.billing_address = billing_address
      if phone_num:
        user_profile.phone_num = phone_num
      user_profile.zipcode = billing_zipcode
      user_profile.save()

      if u.email != receiver.email:
        # if receiver is a different user
        user_profile = receiver.get_profile()
        user_profile.shipping_address = shipping_address
        user_profile.shipping_addresses.add(shipping_address)
        if phone_num:
          user_profile.phone_num = phone_num
        user_profile.zipcode = billing_zipcode
        user_profile.save()

      # create order
      yesterday = datetime.today() - timedelta(days=1)
      order = Order(ordered_by=u, receiver=receiver, cart=cart,
            shipping_address=shipping_address, credit_card=card, order_date=yesterday)
      order.assign_new_order_id()
      order.save()

      update_invoice_date = True
      from_date = datetime.date(datetime.now(tz=UTC()))
      subscriptions = SubscriptionInfo.objects.filter(user=order.receiver).order_by("-updated_datetime")
      if subscriptions.exists() and subscriptions[0].quantity == item.price_category and subscriptions[0].frequency == item.frequency:
        # latest subscription info is valid and use it to update
        subscription = subscriptions[0]
        if subscription.next_invoice_date < date.today():
          from_date = subscription.next_invoice_date
        else:
          update_invoice_date = False
      else:
        # create new subscription info
        subscription = SubscriptionInfo(user=order.receiver,
                                      quantity=item.price_category,
                                      frequency=item.frequency)

      if update_invoice_date:
        if item.frequency == 1:
          next_invoice = from_date + relativedelta(months=+1)
        elif item.frequency == 2:
          next_invoice = from_date + relativedelta(months=+2)
        elif item.frequency == 3:
          next_invoice = from_date + relativedelta(months=+3)
        else:
          # set it to yesterday since subscription cancelled or was one time purchase
          # this way, celery task won't pick things up
          next_invoice = datetime.now(tz=UTC()) - timedelta(days=1)
        subscription.next_invoice_date = next_invoice
      subscription.updated_datetime = datetime.now(tz=UTC())
      subscription.save()

      if suspended:
        order.receiver.get_profile().cancel_subscription()

      # shipped already
      order.fulfill_status = 7
      order.save()

      """
      # Don't send e-mail for now
      # send out verification e-mail, create a verification code
      request = HttpRequest()
      request.META['SERVER_NAME'] = "www.vinely.com"
      request.META['SERVER_PORT'] = 443
      request.user = u
      request.session = {}

      if u.email == receiver.email:
        send_order_added_email(request, order.order_id, u.email, customer_verification_code, customer_temp_password)
      else:
        send_order_added_email(request, order.order_id, u.email, customer_verification_code, customer_temp_password)
        send_order_added_email(request, order.order_id, receiver.email, receiver_verification_code, receiver_temp_password)
      send_to_supplier_order_added_email(request, order.order_id)
      """
