from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from emailusernames.utils import create_user

from optparse import make_option
import types, string, uuid
import xlrd, pytz
from datetime import datetime

from accounts.models import Address, CreditCard, VerificationQueue
from main.models import SubscriptionInfo, CustomizeOrder, Party, PartyInvite
from personality.utils import calculate_wine_personality
from personality.models import WinePersonality, Wine, WineRatingData
from accounts.utils import send_thank_valued_member_email

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
CREDIT_CARD_NUMBER = 19
CREDIT_CARD_EXPIRATION = 20
SUBSCRIPTION_FREQ = 21
PRICE_TIER = 22
QUANTITY = 23
RED_WHITE = 24
SPARKLING = 25
CREDIT_OUTSTANDING = 26
WINE_PERSONALITY = 27
FULFILLMENT_TYPE_A = 28  # like
FULFILLMENT_TYPE_B = 29  # neutral
PARTY_DATE = 30
HOST = 31
VINELY_PRO = 32

WINE_1_OVERALL = 33
WINE_1_SWEET = 34
WINE_1_SWEET_DNL = 35
WINE_1_WEIGHT = 36
WINE_1_WEIGHT_DNL = 37
WINE_1_TEXTURE = 38
WINE_1_TEXTURE_DNL = 39
WINE_1_SIZZLE = 40
WINE_1_SIZZLE_DNL = 41

WINE_2_OVERALL = 42
WINE_2_SWEET = 43
WINE_2_SWEET_DNL = 44
WINE_2_WEIGHT = 45
WINE_2_WEIGHT_DNL = 46
WINE_2_TEXTURE = 47
WINE_2_TEXTURE_DNL = 48
WINE_2_SIZZLE = 49
WINE_2_SIZZLE_DNL = 50

WINE_3_OVERALL = 51
WINE_3_SWEET = 52
WINE_3_SWEET_DNL = 53
WINE_3_WEIGHT = 54
WINE_3_WEIGHT_DNL = 55
WINE_3_TEXTURE = 56
WINE_3_TEXTURE_DNL = 57
WINE_3_SIZZLE = 58
WINE_3_SIZZLE_DNL = 59

WINE_4_OVERALL = 60
WINE_4_SWEET = 61
WINE_4_SWEET_DNL = 62
WINE_4_WEIGHT = 63
WINE_4_WEIGHT_DNL = 64
WINE_4_TEXTURE = 65
WINE_4_TEXTURE_DNL = 66
WINE_4_SIZZLE = 67
WINE_4_SIZZLE_DNL = 68

WINE_5_OVERALL = 69
WINE_5_SWEET = 70
WINE_5_SWEET_DNL = 71
WINE_5_WEIGHT = 72
WINE_5_WEIGHT_DNL = 73
WINE_5_TEXTURE = 74
WINE_5_TEXTURE_DNL = 75
WINE_5_SIZZLE = 76
WINE_5_SIZZLE_DNL = 77

WINE_6_OVERALL = 78
WINE_6_SWEET = 79
WINE_6_SWEET_DNL = 80
WINE_6_WEIGHT = 81
WINE_6_WEIGHT_DNL = 82
WINE_6_TEXTURE = 83
WINE_6_TEXTURE_DNL = 84
WINE_6_SIZZLE = 85
WINE_6_SIZZLE_DNL = 86


class Command(BaseCommand):

  args = ''
  help = 'Ingest the master database of users'

  option_list = BaseCommand.option_list + (
    make_option('-f', '--file',
            type='string',
            dest='filename',
            default=None,
            help='The excel file name of master database.'),
    )



  def handle(self, *args, **options):

    taster_group = Group.objects.get(name="Vinely Taster")
    host_group = Group.objects.get(name="Vinely Host")
    pro_group = Group.objects.get(name="Vinely Pro")

    unknown_address = Address(nick_name="Unknown Address",
                street1="Unknown Street",
                city="Grand Rapids",
                state="MI",
                zipcode="49501")
    unknown_address.save()

    wine1 = Wine.objects.get(id=1)
    wine2 = Wine.objects.get(id=2)
    wine3 = Wine.objects.get(id=3)
    wine4 = Wine.objects.get(id=4)
    wine5 = Wine.objects.get(id=5)
    wine6 = Wine.objects.get(id=6)

    if options['filename']:
      wb = xlrd.open_workbook(options['filename'])
    else:
      wb = xlrd.open_workbook('data/master_db_09132012.xlsx')

    sh = wb.sheet_by_name('Customers202')

    for rownum in range(sh.nrows):
      row = sh.row_values(rownum)
      if type(row[CUSTOMER_ID]) is types.FloatType and row[RECIPIENT_FIRST_NAME]:
        print row[CUSTOMER_ID], row[RECIPIENT_FIRST_NAME]
        try:
          user = User.objects.get(email=row[RECIPIENT_EMAIL])
          if user.first_name:
            user.first_name = row[RECIPIENT_FIRST_NAME]
            user.last_name = row[RECIPIENT_LAST_NAME]
            user.save()
          if user.groups.all().count() == 0:
            user.groups.add(taster_group)
        except User.DoesNotExist:
          # create new user
          user = create_user(row[RECIPIENT_EMAIL], 'welcome')
          user.is_active = False
          user.first_name = row[RECIPIENT_FIRST_NAME]
          user.last_name = row[RECIPIENT_LAST_NAME]
          user.save()
          user.groups.add(taster_group)
          # TODO: create temporary password and send new account e-mail
          # thanking them
          temp_password = User.objects.make_random_password()
          user.set_password(temp_password)
          user.save()

          verification_code = str(uuid.uuid4())
          vque = VerificationQueue(user=user, verification_code=verification_code)
          vque.save()

          # send out verification e-mail, create a verification code
          send_thank_valued_member_email(None, verification_code, temp_password, user.email)


        profile = user.get_profile()
        customer_id = str(int(row[CUSTOMER_ID]))
        profile.vinely_customer_id = customer_id.rjust(6, '0') 

        shipping_address = Address(nick_name="Shipping",
                company_co=row[RECIPIENT_COMPANY],
                street1=row[RECIPIENT_ADDRESS1],
                street2=row[RECIPIENT_ADDRESS2],
                city=row[RECIPIENT_CITY],
                state=row[RECIPIENT_STATE],
                zipcode=row[RECIPIENT_POSTAL_CODE])
        shipping_address.save()
        profile.shipping_address = shipping_address

        billing_address = Address(nick_name="Shipping",
                street1=row[CUSTOMER_ADDRESS],
                city=row[CUSTOMER_CITY],
                state=row[CUSTOMER_STATE],
                zipcode=row[CUSTOMER_POSTAL_CODE])
        billing_address.save()         

        profile.billing_address = billing_address

        if row[CREDIT_CARD_NUMBER]:
          credit_card = CreditCard(nick_name="Primary Card",
                                  card_number=row[CREDIT_CARD_NUMBER],
                                  exp_month=int(row[CREDIT_CARD_EXPIRATION][:2]),
                                  exp_year=int(row[CREDIT_CARD_EXPIRATION][3:5]),
                                  verification_code="XXX",
                                  billing_zipcode=row[CUSTOMER_POSTAL_CODE])

          credit_card.save()

          profile.credit_card = credit_card

        personality_str = string.strip(row[WINE_PERSONALITY])
        if personality_str:
          personality = WinePersonality.objects.get(name=personality_str)
          profile.wine_personality = personality

        profile.save()

        # subscription information
        subscription, created = SubscriptionInfo.objects.get_or_create(user=user)
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
        subscription.frequency = frequency
        subscription.quantity = quantity
        subscription.save()

        if row[RED_WHITE] or row[SPARKLING]:
          customization = CustomizeOrder.objects.get_or_create(user=user)
          if string.strip(row[RED_WHITE]).lower() in ['white']:
            customization.wine_mix = 3 
          elif string.strip(row[RED_WHITE]).lower() in ['red']:
            customization.wine_mix = 2 
          elif string.strip(row[RED_WHITE]).lower() in ['red or white']:
            customization.wine_mix = 1 
          else:
            # vinely recommendation
            customization.wine_mix = 0

          if string.strip(row[SPARKLING]).lower() in ['yes']:
            customization.sparkling = 1 
          else:
            customization.sparkling = 0 
          customization.save()

        # create party
        # create host
        try:
          host = User.objects.get(email=row[HOST]) 
          if host.groups.all().count() == 0:
            host.groups.add(host_group)
        except User.DoesNotExist:
          print "Host email", rownum, row[HOST]
          host = create_user(row[HOST], 'welcome')
          host.is_active = False 
          host.save() 
          host.groups.add(host_group)

        date_tuple = xlrd.xldate_as_tuple(row[PARTY_DATE], 0)
        event_date = datetime(*date_tuple)
        party, created = Party.objects.get_or_create(host=host, title="%s's party" % row[HOST], 
                                  address=unknown_address,
                                  event_date=event_date)
        if created:
          party.created = event_date
          party.save()

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

        wine1_rating.overall = int(row[WINE_1_OVERALL])
        wine1_rating.sweet = int(row[WINE_1_SWEET])
        wine1_rating.sweet_dnl = int(row[WINE_1_SWEET_DNL])
        wine1_rating.weight = int(row[WINE_1_WEIGHT])
        wine1_rating.weight_dnl = int(row[WINE_1_WEIGHT_DNL])        
        wine1_rating.texture = int(row[WINE_1_TEXTURE])
        wine1_rating.texture_dnl = int(row[WINE_1_TEXTURE_DNL])
        wine1_rating.sizzle = int(row[WINE_1_SIZZLE])
        wine1_rating.sizzle_dnl = int(row[WINE_1_SIZZLE_DNL])       
        wine1_rating.save()

        wine2_rating.overall = int(row[WINE_2_OVERALL])
        wine2_rating.sweet = int(row[WINE_2_SWEET])
        wine2_rating.sweet_dnl = int(row[WINE_2_SWEET_DNL])
        wine2_rating.weight = int(row[WINE_2_WEIGHT])
        wine2_rating.weight_dnl = int(row[WINE_2_WEIGHT_DNL])        
        wine2_rating.texture = int(row[WINE_2_TEXTURE])
        wine2_rating.texture_dnl = int(row[WINE_2_TEXTURE_DNL])
        wine2_rating.sizzle = int(row[WINE_2_SIZZLE])
        wine2_rating.sizzle_dnl = int(row[WINE_2_SIZZLE_DNL])       
        wine2_rating.save()

        wine3_rating.overall = int(row[WINE_3_OVERALL])
        wine3_rating.sweet = int(row[WINE_3_SWEET])
        wine3_rating.sweet_dnl = int(row[WINE_3_SWEET_DNL])
        wine3_rating.weight = int(row[WINE_3_WEIGHT])
        wine3_rating.weight_dnl = int(row[WINE_3_WEIGHT_DNL])        
        wine3_rating.texture = int(row[WINE_3_TEXTURE])
        wine3_rating.texture_dnl = int(row[WINE_3_TEXTURE_DNL])
        wine3_rating.sizzle = int(row[WINE_3_SIZZLE])
        wine3_rating.sizzle_dnl = int(row[WINE_3_SIZZLE_DNL])              
        wine3_rating.save()

        wine4_rating.overall = int(row[WINE_4_OVERALL])
        wine4_rating.sweet = int(row[WINE_4_SWEET])
        wine4_rating.sweet_dnl = int(row[WINE_4_SWEET_DNL])
        wine4_rating.weight = int(row[WINE_4_WEIGHT])
        wine4_rating.weight_dnl = int(row[WINE_4_WEIGHT_DNL])        
        wine4_rating.texture = int(row[WINE_4_TEXTURE])
        wine4_rating.texture_dnl = int(row[WINE_4_TEXTURE_DNL])
        wine4_rating.sizzle = int(row[WINE_4_SIZZLE])
        wine4_rating.sizzle_dnl = int(row[WINE_4_SIZZLE_DNL])                     
        wine4_rating.save()

        wine5_rating.overall = int(row[WINE_5_OVERALL])
        wine5_rating.sweet = int(row[WINE_5_SWEET])
        wine5_rating.sweet_dnl = int(row[WINE_5_SWEET_DNL])
        wine5_rating.weight = int(row[WINE_5_WEIGHT])
        wine5_rating.weight_dnl = int(row[WINE_5_WEIGHT_DNL])        
        wine5_rating.texture = int(row[WINE_5_TEXTURE])
        wine5_rating.texture_dnl = int(row[WINE_5_TEXTURE_DNL])
        wine5_rating.sizzle = int(row[WINE_5_SIZZLE])
        wine5_rating.sizzle_dnl = int(row[WINE_5_SIZZLE_DNL])                     
        wine5_rating.save()

        wine6_rating.overall = int(row[WINE_6_OVERALL])
        wine6_rating.sweet = int(row[WINE_6_SWEET])
        wine6_rating.sweet_dnl = int(row[WINE_6_SWEET_DNL])
        wine6_rating.weight = int(row[WINE_6_WEIGHT])
        wine6_rating.weight_dnl = int(row[WINE_6_WEIGHT_DNL])        
        wine6_rating.texture = int(row[WINE_6_TEXTURE])
        wine6_rating.texture_dnl = int(row[WINE_6_TEXTURE_DNL])
        wine6_rating.sizzle = int(row[WINE_6_SIZZLE])
        wine6_rating.sizzle_dnl = int(row[WINE_6_SIZZLE_DNL])                            
        wine6_rating.save()

        if not personality_str:
          # saves new wine personality
          personality = calculate_wine_personality(user, wine1_rating, wine2_rating,
                                      wine3_rating, wine4_rating,
                                      wine5_rating, wine6_rating)

