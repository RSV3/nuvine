from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.http import HttpRequest

from emailusernames.utils import create_user

from optparse import make_option
import types, string, uuid
import xlrd
import numpy as np
from datetime import datetime
from creditcard.utils import get_cc_type

from accounts.models import Address, CreditCard, VerificationQueue, UserProfile
from main.models import SubscriptionInfo, CustomizeOrder, Party, PartyInvite, MyHost, OrganizedParty
from personality.utils import calculate_wine_personality
from personality.models import WinePersonality, Wine, WineRatingData
from accounts.utils import send_thank_valued_member_email
from lepl.apps.rfc3696 import Email

from main.utils import UTC


CUSTOMER_ID = 0
RECIPIENT_FIRST_NAME = 1
RECIPIENT_LAST_NAME = 2
RECIPIENT_COMPANY = 3
RECIPIENT_ADDRESS1 = 4
RECIPIENT_ADDRESS2 = 5
RECIPIENT_CITY = 6
RECIPIENT_STATE = 7
RECIPIENT_POSTAL_CODE = 8
RECIPIENT_COUNTRY = 9
RECIPIENT_HOME_PHONE = 10
RECIPIENT_WORK_PHONE = 11
RECIPIENT_EMAIL = 12

CUSTOMER_FIRST_NAME = 13
CUSTOMER_LAST_NAME = 14
CUSTOMER_ADDRESS = 15
CUSTOMER_CITY = 16
CUSTOMER_STATE = 17
CUSTOMER_POSTAL_CODE = 18
CREDIT_CARD_TYPE = 19
CREDIT_CARD_NUMBER = 20
CREDIT_CARD_CVV = 21
CREDIT_CARD_EXPIRATION = 22
BILLING_ZIPCODE = 23

FIRST_PARTY_DATE = 24
HOST_EMAIL = 25
VINELY_PRO_EMAIL = 26

SUBSCRIPTION_FREQ = 27
PRICE_TIER = 28
QUANTITY = 29
RED_WHITE = 30
SPARKLING = 31
CREDIT_OUTSTANDING = 32
WINE_PERSONALITY = 33
FULFILLMENT_TYPE_A = 34  # like
FULFILLMENT_TYPE_B = 35  # neutral

WINE_1_OVERALL = 36
WINE_1_SWEET = 38
WINE_1_SWEET_DNL = 39
WINE_1_WEIGHT = 40
WINE_1_WEIGHT_DNL = 41
WINE_1_TEXTURE = 42
WINE_1_TEXTURE_DNL = 43
WINE_1_SIZZLE = 44
WINE_1_SIZZLE_DNL = 45

WINE_2_OVERALL = 47
WINE_2_SWEET = 49
WINE_2_SWEET_DNL = 50
WINE_2_WEIGHT = 51
WINE_2_WEIGHT_DNL = 52
WINE_2_TEXTURE = 53
WINE_2_TEXTURE_DNL = 54
WINE_2_SIZZLE = 55
WINE_2_SIZZLE_DNL = 56

WINE_3_OVERALL = 58
WINE_3_SWEET = 60
WINE_3_SWEET_DNL = 61
WINE_3_WEIGHT = 62
WINE_3_WEIGHT_DNL = 63
WINE_3_TEXTURE = 64
WINE_3_TEXTURE_DNL = 65
WINE_3_SIZZLE = 66
WINE_3_SIZZLE_DNL = 67

WINE_4_OVERALL = 69
WINE_4_SWEET = 71
WINE_4_SWEET_DNL = 72
WINE_4_WEIGHT = 73
WINE_4_WEIGHT_DNL = 74
WINE_4_TEXTURE = 75
WINE_4_TEXTURE_DNL = 76
WINE_4_SIZZLE = 77
WINE_4_SIZZLE_DNL = 78

WINE_5_OVERALL = 80
WINE_5_SWEET = 82
WINE_5_SWEET_DNL = 83
WINE_5_WEIGHT = 84
WINE_5_WEIGHT_DNL = 85
WINE_5_TEXTURE = 86
WINE_5_TEXTURE_DNL = 87
WINE_5_SIZZLE = 88
WINE_5_SIZZLE_DNL = 89

WINE_6_OVERALL = 91
WINE_6_SWEET = 93
WINE_6_SWEET_DNL = 94
WINE_6_WEIGHT = 95
WINE_6_WEIGHT_DNL = 96
WINE_6_TEXTURE = 97
WINE_6_TEXTURE_DNL = 98
WINE_6_SIZZLE = 99
WINE_6_SIZZLE_DNL = 100


class Command(BaseCommand):

  args = ''
  help = 'Ingest the master database of users'

  option_list = BaseCommand.option_list + (
    make_option('-f', '--file',
              type='string',
              dest='filename',
              default=None,
              help='The excel file name of master database.'),
    make_option('-j', '--hosts',
                      action='store_true',
                      dest='hosts',
                      default=False,
                      help="Import host users and send them welcome an e-mail."),
  )



  def handle(self, *args, **options):

    taster_group = Group.objects.get(name="Vinely Taster")
    host_group = Group.objects.get(name="Vinely Host")
    pro_group = Group.objects.get(name="Vinely Pro")

    elizabeth = User.objects.get(email="elizabeth@vinely.com")

    # used for party info
    unknown_address_MI = Address(nick_name="Unknown Address",
                street1="Unknown Street",
                city="Grand Rapids",
                state="MI",
                zipcode="49501")
    unknown_address_MI.save()

    unknown_address_MA = Address(nick_name="Unknown Address",
                street1="Unknown Street",
                city="Cambridge",
                state="MA",
                zipcode="02139")
    unknown_address_MA.save()

    unknown_address_CA = Address(nick_name="Unknown Address",
                street1="Unknown Street",
                city="Cambridge",
                state="CA",
                zipcode="94117")
    unknown_address_CA.save()

    wine1 = Wine.objects.get(id=1)
    wine2 = Wine.objects.get(id=2)
    wine3 = Wine.objects.get(id=3)
    wine4 = Wine.objects.get(id=4)
    wine5 = Wine.objects.get(id=5)
    wine6 = Wine.objects.get(id=6)

    email_validator = Email()

    if options['filename']:
      wb = xlrd.open_workbook(options['filename'])
    else:
      wb = xlrd.open_workbook('data/customer_ingest_11092012.xlsx')

    sh = wb.sheet_by_name('Customers')

    if options['hosts']:
      host_emails = set()

      for rownum in range(sh.nrows):
        row = sh.row_values(rownum)
        # only send e-mails to the hosts

        if email_validator(row[HOST_EMAIL]):
          host_emails.add(row[HOST_EMAIL])

      for host_email in list(host_emails):
        try:
          host = User.objects.get(email=host_email)
          host_profile = host.get_profile()
          if host_profile.role == UserProfile.ROLE_CHOICES[0][0]:
            host_profile.role = UserProfile.ROLE_CHOICES[2][0]
            host_profile.save()
        except User.DoesNotExist:
          print "Host email", rownum, host_email
          host = create_user(host_email, 'welcome')
          host.is_active = False
          host.save()

        import_date = datetime(2012, 11, 16, 22, 50, 55, 540321, tzinfo=UTC())
        if host.last_login < import_date:
          temp_password = User.objects.make_random_password()
          host.set_password(temp_password)
          host.save()

          verification_code = str(uuid.uuid4())
          vque = VerificationQueue(user=host, verification_code=verification_code)
          vque.save()

          request = HttpRequest()
          request.META['SERVER_NAME'] = "www.vinely.com"
          request.META['SERVER_PORT'] = 80
          request.user = host
          request.session = {}

          # send out verification e-mail, create a verification code
          send_thank_valued_member_email(request, verification_code, temp_password, host)
    else:

      for rownum in range(sh.nrows):
        row = sh.row_values(rownum)
        if type(row[CUSTOMER_ID]) is types.FloatType and row[RECIPIENT_FIRST_NAME]:
          print row[CUSTOMER_ID], row[RECIPIENT_FIRST_NAME]
          customer_email = row[RECIPIENT_EMAIL].strip().lower()
          try:
            user = User.objects.get(email=customer_email)
            if not user.first_name:
              user.first_name = row[RECIPIENT_FIRST_NAME]
              user.last_name = row[RECIPIENT_LAST_NAME]
              user.save()
            profile = user.get_profile()
            if profile.role == UserProfile.ROLE_CHOICES[0][0]:
              profile.role = UserProfile.ROLE_CHOICES[3][0]
              profile.save()
          except User.DoesNotExist:
            # create new user
            user = create_user(customer_email, 'welcome')
            user.is_active = False
            user.first_name = row[RECIPIENT_FIRST_NAME]
            user.last_name = row[RECIPIENT_LAST_NAME]
            user.save()
            profile = user.get_profile()
            profile.role = UserProfile.ROLE_CHOICES[3][0]
            profile.save()
            # TODO: create temporary password and send new account e-mail
            # thanking them
            temp_password = User.objects.make_random_password()
            user.set_password(temp_password)
            user.save()

            verification_code = str(uuid.uuid4())
            vque = VerificationQueue(user=user, verification_code=verification_code)
            vque.save()

            request = HttpRequest()
            request.META['SERVER_NAME'] = "www.vinely.com"
            request.META['SERVER_PORT'] = 80
            request.user = user
            request.session = {}

            # send out verification e-mail, create a verification code
            send_thank_valued_member_email(request, verification_code, temp_password, user)

          profile = user.get_profile()

          if row[RECIPIENT_HOME_PHONE]:
            profile.phone = row[RECIPIENT_HOME_PHONE].strip()
          if row[RECIPIENT_WORK_PHONE]:
            profile.work_phone = row[RECIPIENT_WORK_PHONE].strip()

          #customer_id = str(int(row[CUSTOMER_ID]))
          #profile.vinely_customer_id = customer_id.rjust(7, '0')
          if profile.zipcode is None and row[CUSTOMER_POSTAL_CODE]:
            billing_zipcode = str(int(row[CUSTOMER_POSTAL_CODE])).rjust(5, '0')
            profile.zipcode = billing_zipcode
          else:
            billing_zipcode = ""
          if row[RECIPIENT_POSTAL_CODE]:
            recipient_zipcode = str(int(row[RECIPIENT_POSTAL_CODE])).rjust(5, '0')
          else:
            recipient_zipcode = ""

          shipping_address = Address(nick_name="Shipping",
                  company_co=row[RECIPIENT_COMPANY],
                  street1=row[RECIPIENT_ADDRESS1],
                  street2=row[RECIPIENT_ADDRESS2],
                  city=row[RECIPIENT_CITY],
                  state=row[RECIPIENT_STATE],
                  zipcode=recipient_zipcode)
          shipping_address.save()
          profile.shipping_address = shipping_address

          billing_address = Address(nick_name="Shipping",
                  street1=row[CUSTOMER_ADDRESS],
                  city=row[CUSTOMER_CITY],
                  state=row[CUSTOMER_STATE],
                  zipcode=billing_zipcode)
          billing_address.save()

          profile.billing_address = billing_address

          if row[CREDIT_CARD_NUMBER]:
            # create credit card
            card_num = str(int(row[CREDIT_CARD_NUMBER])).strip()
            cvv_num = str(int(row[CREDIT_CARD_CVV]) if row[CREDIT_CARD_CVV] else row[CREDIT_CARD_CVV]).strip()
            card_type = get_cc_type(int(row[CREDIT_CARD_NUMBER]))

            billing_zipcode = row[BILLING_ZIPCODE]
            if not billing_zipcode:
              billing_zipcode = row[CUSTOMER_POSTAL_CODE]

            exp_date = datetime.strptime(row[CREDIT_CARD_EXPIRATION].strip(), "%m/%y")
            credit_card = CreditCard(nick_name=customer_email, card_number=card_num,
                        exp_month=exp_date.month, exp_year=exp_date.year, verification_code=cvv_num,
                        billing_zipcode=str(int(billing_zipcode)).zfill(5),
                        card_type=card_type)
            credit_card.save()
            # encrypt card number
            credit_card.encrypt_card_num(card_num)
            credit_card.encrypt_cvv(cvv_num)
            credit_card.save()

            profile.credit_card = credit_card

          personality_str = string.strip(row[WINE_PERSONALITY])
          if personality_str:
            personality = WinePersonality.objects.get(name=personality_str)
            profile.wine_personality = personality

          profile.save()

          # subscription information
          subscriptions = SubscriptionInfo.objects.filter(user=user)

          if not subscriptions.exists():
            # update only if they have no subscription
            frequency = 9
            quantity = 0
            if string.strip(row[SUBSCRIPTION_FREQ]).lower() in ['once', 'one time']:
              frequency = 0
            elif string.strip(row[SUBSCRIPTION_FREQ]).lower() == 'monthly':
              frequency = 1
            elif string.strip(row[SUBSCRIPTION_FREQ]).lower() == 'bi-monthly':
              frequency = 2
            elif string.strip(row[SUBSCRIPTION_FREQ]).lower() == 'quarterly':
              frequency = 3

            if string.strip(row[PRICE_TIER]).lower() in ['good', 'basic']:
              if int(row[QUANTITY]) == 6:
                quantity = 6
              elif int(row[QUANTITY]) == 12:
                quantity = 5
            elif string.strip(row[PRICE_TIER]).lower() in ['better', 'superior']:
              if int(row[QUANTITY]) == 6:
                quantity = 8
              elif int(row[QUANTITY]) == 12:
                quantity = 7
            elif string.strip(row[PRICE_TIER]).lower() in ['best', 'divine']:
              if int(row[QUANTITY]) == 6:
                quantity = 10
              elif int(row[QUANTITY]) == 12:
                quantity = 9

            subscription = SubscriptionInfo(user=user, frequency=frequency, quantity=quantity)
            subscription.save()

          if row[RED_WHITE] or row[SPARKLING]:
            customization, created = CustomizeOrder.objects.get_or_create(user=user)
            if string.strip(row[RED_WHITE]).lower() in ['white']:
              customization.wine_mix = 3
            elif string.strip(row[RED_WHITE]).lower() in ['red']:
              customization.wine_mix = 2
            elif string.strip(row[RED_WHITE]).lower() in ['red or white']:
              customization.wine_mix = 1
            else:
              # vinely recommendation
              customization.wine_mix = 0

            if string.strip(row[SPARKLING]).lower() in ['no']:
              customization.sparkling = 0
            else:
              customization.sparkling = 1
            customization.save()

          # create party
          # create host
          if row[HOST_EMAIL]:
            try:
              host = User.objects.get(email=row[HOST_EMAIL])
              host_profile = host.get_profile()
              if host_profile.role == UserProfile.ROLE_CHOICES[0][0]:
                host_profile.role = UserProfile.ROLE_CHOICES[2][0]
                host_profile.save()
            except User.DoesNotExist:
              print "Host email", rownum, row[HOST_EMAIL]
              host = create_user(row[HOST_EMAIL], 'welcome')
              host.is_active = True
              host.save()

              host_profile = host.get_profile()
              host_profile.role = UserProfile.ROLE_CHOICES[2][0]
              host_profile.save()

              pro_assignment, created = MyHost.objects.get_or_create(host=host)
              if pro_assignment.pro is None:
                pro_assignment.pro = elizabeth
              pro_assignment.save()

            date_tuple = xlrd.xldate_as_tuple(row[FIRST_PARTY_DATE], 0)
            event_date = datetime(*date_tuple, tzinfo=UTC())
            created = None

            if row[RECIPIENT_STATE].strip() in ['CA']:
              party, created = Party.objects.get_or_create(host=host, title="%s's party" % row[HOST_EMAIL],
                                        address=unknown_address_CA,
                                        event_date=event_date)


            elif row[RECIPIENT_STATE].strip() in ['MA']:
              party, created = Party.objects.get_or_create(host=host, title="%s's party" % row[HOST_EMAIL],
                                        address=unknown_address_MA,
                                        event_date=event_date)
            else:
              party, created = Party.objects.get_or_create(host=host, title="%s's party" % row[HOST_EMAIL],
                                        address=unknown_address_MI,
                                        event_date=event_date)
            if created:
              party.created = event_date
              party.save()
              party_pro = OrganizedParty(pro=elizabeth, party=party)
              party_pro.timestamp = event_date
              party_pro.save()

            # create party invite
            invite, created = PartyInvite.objects.get_or_create(party=party, invitee=user)
            invite.response = 3
            invite.save()

          # save wine rating data

          wine1_rating, created = WineRatingData.objects.get_or_create(user=user, wine=wine1)
          wine2_rating, created = WineRatingData.objects.get_or_create(user=user, wine=wine2)
          wine3_rating, created = WineRatingData.objects.get_or_create(user=user, wine=wine3)
          wine4_rating, created = WineRatingData.objects.get_or_create(user=user, wine=wine4)
          wine5_rating, created = WineRatingData.objects.get_or_create(user=user, wine=wine5)
          wine6_rating, created = WineRatingData.objects.get_or_create(user=user, wine=wine6)

          wine1_rating.overall = int(row[WINE_1_OVERALL] if row[WINE_1_OVERALL] else 0)
          wine1_rating.sweet = int(row[WINE_1_SWEET] if row[WINE_1_SWEET] else 0)
          wine1_rating.sweet_dnl = int(row[WINE_1_SWEET_DNL] if row[WINE_1_SWEET_DNL] else 0)
          wine1_rating.weight = int(row[WINE_1_WEIGHT] if row[WINE_1_WEIGHT] else 0)
          wine1_rating.weight_dnl = int(row[WINE_1_WEIGHT_DNL] if row[WINE_1_WEIGHT_DNL] else 0)
          wine1_rating.texture = int(row[WINE_1_TEXTURE] if row[WINE_1_TEXTURE] else 0)
          wine1_rating.texture_dnl = int(row[WINE_1_TEXTURE_DNL] if row[WINE_1_TEXTURE_DNL] else 0)
          wine1_rating.sizzle = int(row[WINE_1_SIZZLE] if row[WINE_1_SIZZLE] else 0)
          wine1_rating.sizzle_dnl = int(row[WINE_1_SIZZLE_DNL] if row[WINE_1_SIZZLE_DNL] else 0)
          wine1_rating.save()

          wine2_rating.overall = int(row[WINE_2_OVERALL] if row[WINE_2_OVERALL] else 0)
          wine2_rating.sweet = int(row[WINE_2_SWEET] if row[WINE_2_SWEET] else 0)
          wine2_rating.sweet_dnl = int(row[WINE_2_SWEET_DNL] if row[WINE_2_SWEET_DNL] else 0)
          wine2_rating.weight = int(row[WINE_2_WEIGHT] if row[WINE_2_WEIGHT] else 0)
          wine2_rating.weight_dnl = int(row[WINE_2_WEIGHT_DNL] if row[WINE_2_WEIGHT_DNL] else 0)
          wine2_rating.texture = int(row[WINE_2_TEXTURE] if row[WINE_2_TEXTURE] else 0)
          wine2_rating.texture_dnl = int(row[WINE_2_TEXTURE_DNL] if row[WINE_2_TEXTURE_DNL] else 0)
          wine2_rating.sizzle = int(row[WINE_2_SIZZLE] if row[WINE_2_SIZZLE] else 0)
          wine2_rating.sizzle_dnl = int(row[WINE_2_SIZZLE_DNL] if row[WINE_2_SIZZLE_DNL] else 0)
          wine2_rating.save()

          wine3_rating.overall = int(row[WINE_3_OVERALL] if row[WINE_3_OVERALL] else 0)
          wine3_rating.sweet = int(row[WINE_3_SWEET] if row[WINE_3_SWEET] else 0)
          wine3_rating.sweet_dnl = int(row[WINE_3_SWEET_DNL] if row[WINE_3_SWEET_DNL] else 0)
          wine3_rating.weight = int(row[WINE_3_WEIGHT] if row[WINE_3_WEIGHT] else 0)
          wine3_rating.weight_dnl = int(row[WINE_3_WEIGHT_DNL] if row[WINE_3_WEIGHT_DNL] else 0)
          wine3_rating.texture = int(row[WINE_3_TEXTURE] if row[WINE_3_TEXTURE] else 0)
          wine3_rating.texture_dnl = int(row[WINE_3_TEXTURE_DNL] if row[WINE_3_TEXTURE_DNL] else 0)
          wine3_rating.sizzle = int(row[WINE_3_SIZZLE] if row[WINE_3_SIZZLE] else 0)
          wine3_rating.sizzle_dnl = int(row[WINE_3_SIZZLE_DNL] if row[WINE_3_SIZZLE_DNL] else 0)
          wine3_rating.save()

          wine4_rating.overall = int(row[WINE_4_OVERALL] if row[WINE_4_OVERALL] else 0)
          wine4_rating.sweet = int(row[WINE_4_SWEET] if row[WINE_4_SWEET] else 0)
          wine4_rating.sweet_dnl = int(row[WINE_4_SWEET_DNL] if row[WINE_4_SWEET_DNL] else 0)
          wine4_rating.weight = int(row[WINE_4_WEIGHT] if row[WINE_4_WEIGHT] else 0)
          wine4_rating.weight_dnl = int(row[WINE_4_WEIGHT_DNL] if row[WINE_4_WEIGHT_DNL] else 0)
          wine4_rating.texture = int(row[WINE_4_TEXTURE] if row[WINE_4_TEXTURE] else 0)
          wine4_rating.texture_dnl = int(row[WINE_4_TEXTURE_DNL] if row[WINE_4_TEXTURE_DNL] else 0)
          wine4_rating.sizzle = int(row[WINE_4_SIZZLE] if row[WINE_4_SIZZLE] else 0)
          wine4_rating.sizzle_dnl = int(row[WINE_4_SIZZLE_DNL] if row[WINE_4_SIZZLE_DNL] else 0)
          wine4_rating.save()

          wine5_rating.overall = int(row[WINE_5_OVERALL] if row[WINE_5_OVERALL] else 0)
          wine5_rating.sweet = int(row[WINE_5_SWEET] if row[WINE_5_SWEET] else 0)
          wine5_rating.sweet_dnl = int(row[WINE_5_SWEET_DNL] if row[WINE_5_SWEET_DNL] else 0)
          wine5_rating.weight = int(row[WINE_5_WEIGHT] if row[WINE_5_WEIGHT] else 0)
          wine5_rating.weight_dnl = int(row[WINE_5_WEIGHT_DNL] if row[WINE_5_WEIGHT_DNL] else 0)
          wine5_rating.texture = int(row[WINE_5_TEXTURE] if row[WINE_5_TEXTURE] else 0)
          wine5_rating.texture_dnl = int(row[WINE_5_TEXTURE_DNL] if row[WINE_5_TEXTURE_DNL] else 0)
          wine5_rating.sizzle = int(row[WINE_5_SIZZLE] if row[WINE_5_SIZZLE] else 0)
          wine5_rating.sizzle_dnl = int(row[WINE_5_SIZZLE_DNL] if row[WINE_5_SIZZLE_DNL] else 0)
          wine5_rating.save()

          wine6_rating.overall = int(row[WINE_6_OVERALL] if row[WINE_6_OVERALL] else 0)
          wine6_rating.sweet = int(row[WINE_6_SWEET] if row[WINE_6_SWEET] else 0)
          wine6_rating.sweet_dnl = int(row[WINE_6_SWEET_DNL] if row[WINE_6_SWEET_DNL] else 0)
          wine6_rating.weight = int(row[WINE_6_WEIGHT] if row[WINE_6_WEIGHT] else 0)
          wine6_rating.weight_dnl = int(row[WINE_6_WEIGHT_DNL] if row[WINE_6_WEIGHT_DNL] else 0)
          wine6_rating.texture = int(row[WINE_6_TEXTURE] if row[WINE_6_TEXTURE] else 0)
          wine6_rating.texture_dnl = int(row[WINE_6_TEXTURE_DNL] if row[WINE_6_TEXTURE_DNL] else 0)
          wine6_rating.sizzle = int(row[WINE_6_SIZZLE] if row[WINE_6_SIZZLE] else 0)
          wine6_rating.sizzle_dnl = int(row[WINE_6_SIZZLE_DNL] if row[WINE_6_SIZZLE_DNL] else 0)
          wine6_rating.save()

          #if not personality_str:
            # saves new wine personality
          # recalculate all wine personality
          if np.sum([wine1_rating.overall, wine2_rating.overall,
                      wine3_rating.overall, wine4_rating.overall,
                      wine5_rating.overall, wine6_rating.overall]) >= 6:
            personality = calculate_wine_personality(user, wine1_rating, wine2_rating,
                                          wine3_rating, wine4_rating,
                                          wine5_rating, wine6_rating)

