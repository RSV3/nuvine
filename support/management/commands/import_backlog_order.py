from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.http import HttpRequest

from optparse import make_option
from datetime import datetime, timedelta

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

SUBSCRIPTION_FREQ = 93
PRICE_TIER = 94
QUANTITY = 95
RED_WHITE = 96
SPARKLING = 97
WINE_PERSONALITY = 99


def get_subscription_frequency(subscription_str):
  if subscription_str.strip().lower() == "one time":
    return 0
  elif subscription_str.strip().lower() == "monthly":
    return 1
  elif subscription_str.strip().lower() == "bi-monthly":
    return 2
  elif subscription_str.strip().lower() == "quarterly":
    return 3

def get_subscription_quantity(price_tier, quantity_float, rownum=0):
  """
    rownum when imported from Excel file
  """
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

    wb = xlrd.open_workbook("data/new_orders_10292012.xlsx")
    sheet = wb.sheet_by_name("Orders")

    for rownum in range(1, 6):
      print "Processing row: %d" % rownum
      row = sheet.row_values(rownum)
      # find user first

      customer_email = row[CUSTOMER_EMAIL].strip().lower()
      # check if valid e-mail exists
      if not email_validator(customer_email):
        # go to next line
        continue

      try:
        u = User.objects.get(email=customer_email)
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
      if u.email == row[RECIPIENT_EMAIL].strip().lower():
        receiver = u
      else:
        # check to see if receiver already has account
        recipient_email = row[RECIPIENT_EMAIL].strip().lower()
        try:
          receiver = User.objects.get(email=recipient_email)
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

      item = LineItem(product=product, price_category=price_category, quantity=quantity_code)
      item.save()

      cart = Cart(user=u, adds=1)
      cart.save()
      cart.items.add(item)
      cart.save()

      customize, created = CustomizeOrder.objects.get_or_create(user=receiver)
      wine_mix_choice = row[RED_WHITE].strip().lower()
      if wine_mix_choice == "vinely":
        customize.wine_mix = 0
      elif wine_mix_choice == "both":
        customize.wine_mix = 1
      elif wine_mix_choice == "red":
        customize.wine_mix = 2
      elif wine_mix_choice == "white":
        customize.wine_mix = 3
      sparkling_choice = row[SPARKLING].strip().lower()
      customize.sparkling = 0 if sparkling_choice == "no" else 1
      customize.save()

      # save customization for customer who ordered if different
      if u != receiver:
        customize, created = CustomizeOrder.objects.get_or_create(user=u)
        wine_mix_choice = row[RED_WHITE].strip().lower()
        if wine_mix_choice == "vinely":
          customize.wine_mix = 0
        elif wine_mix_choice == "both":
          customize.wine_mix = 1
        elif wine_mix_choice == "red":
          customize.wine_mix = 2
        elif wine_mix_choice == "white":
          customize.wine_mix = 3
        sparkling_choice = row[SPARKLING].strip().lower()
        customize.sparkling = 0 if sparkling_choice == "no" else 1
        customize.save()

      # create shipping address
      company_co = row[RECIPIENT_COMPANY]
      if not company_co and customer_full_name != receiver_full_name:
        company_co = receiver_full_name
      if u.email == receiver.email and u.first_name != row[RECIPIENT_FIRST_NAME].strip():
        # need to use the c/o
        shipping_address = Address(nick_name=receiver_full_name, company_co=company_co,
                          street1=row[RECIPIENT_ADDRESS_1], street2=row[RECIPIENT_ADDRESS_2],
                          city=row[RECIPIENT_CITY], state=row[RECIPIENT_STATE], zipcode=str(int(row[RECIPIENT_ZIPCODE])).zfill(5))

      else:
        # use customer's address
        shipping_address = Address(nick_name=customer_full_name, company_co=company_co,
                          street1=row[RECIPIENT_ADDRESS_1], street2=row[RECIPIENT_ADDRESS_2],
                          city=row[RECIPIENT_CITY], state=row[RECIPIENT_STATE], zipcode=str(int(row[RECIPIENT_ZIPCODE])).zfill(5))

      shipping_address.save()

      billing_address = Address(nick_name=customer_full_name,
                                street1=row[CUSTOMER_ADDRESS], city=row[CUSTOMER_CITY],
                                state=row[CUSTOMER_STATE], zipcode=str(int(row[CUSTOMER_ZIPCODE])).zfill(5))
      billing_address.save()

      # create credit card
      card_num = row[CREDIT_CARD_NUM].strip()
      cvv_num = row[CREDIT_CARD_CVV].strip()
      card_type = get_cc_type(row[CREDIT_CARD_NUM])

      billing_zipcode = row[BILLING_ZIPCODE]
      if not billing_zipcode:
        billing_zipcode = row[CUSTOMER_ZIPCODE]
      exp_date = datetime.strptime(row[CREDIT_CARD_EXP], "%m/%y")
      card = CreditCard(nick_name=customer_email, card_number=card_num,
                  exp_month=exp_date.month, exp_year=exp_date.year, verification_code=cvv_num,
                  billing_zipcode=str(int(billing_zipcode)).zfill(5),
                  card_type=card_type)
      card.save()
      # encrypt card number
      card.encrypt_card_num(card_num)
      card.encrypt_cvv(cvv_num)
      card.save()

      # add shipping address to user account
      user_profile = u.get_profile()
      user_profile.shipping_address = shipping_address
      user_profile.shipping_addresses.add(shipping_address)
      user_profile.credit_card = card
      user_profile.credit_cards.add(card)
      user_profile.billing_address = billing_address
      user_profile.save()

      if u.email != receiver.email:
        # if receiver is a different user
        user_profile = receiver.get_profile()
        user_profile.shipping_address = shipping_address
        user_profile.shipping_addresses.add(shipping_address)
        user_profile.save()

      # create order
      order = Order(ordered_by=u, receiver=receiver, cart=cart,
            shipping_address=shipping_address, credit_card=card)
      order.assign_new_order_id()
      order.save()

      subscription, created = SubscriptionInfo.objects.get_or_create(user=order.receiver, quantity=item.price_category,
                                                                    frequency=item.frequency)
      next_invoice = datetime.date(datetime.now(tz=UTC())) + timedelta(days=28)
      subscription.next_invoice_date = next_invoice
      subscription.updated_datetime = datetime.now(tz=UTC())
      subscription.save()

      # shipped already
      order.fulfill_status = 6
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
