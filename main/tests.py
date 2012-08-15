"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.core.files import File
from accounts.models import Address

from main.models import ContactReason, ContactRequest, Party, PartyInvite, Product
from personality.models import Wine, WinePersonality
from emailusernames.utils import create_user, create_superuser

import random
from datetime import date, datetime, timedelta

class SimpleTest(TestCase):
  
  def runTest(self):
    pass

  def create_usable_accounts(self):
    """
      create usable accounts
    """
    ps_group, created = Group.objects.get_or_create(name="Vinely Pro")
    ph_group, created = Group.objects.get_or_create(name="Vinely Socializer")
    att_group, created = Group.objects.get_or_create(name="Vinely Taster")
    supp_group, created = Group.objects.get_or_create(name="Supplier")


    u = create_user("elizabeth@redstar.com", "egoede")
    u.groups.add(ps_group)

    u = create_user("johnstecco@gmail.com", "jstecco")
    u.groups.add(ps_group)

    u = create_user("specialist1@example.com", "hello")
    u.groups.add(ps_group)

    u = create_user("specialist2@example.com", "hello")
    u.groups.add(ps_group)

    u = create_user("host1@example.com", "hello")
    u.groups.add(ph_group)

    u = create_user("host2@example.com", "hello")
    u.groups.add(ph_group)

    u = create_user("host3@example.com", "hello")
    u.groups.add(ph_group)

    u = create_user("attendee1@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee2@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee3@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee4@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee5@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee6@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee7@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee8@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("attendee9@example.com", "hello")
    u.groups.add(att_group)

    u = create_user("supplier1@example.com", "hello")
    u.groups.add(supp_group)

    u = create_user("supplier2@example.com", "hello")
    u.groups.add(supp_group)

    suppliers = User.objects.filter(groups=supp_group)
    self.assertEqual(suppliers.count(), 2)

    tasters = User.objects.filter(groups=att_group)
    self.assertEqual(tasters.count(), 9)

    for u in User.objects.all():
      u.is_active = True
      u.save()


  def create_wine_personalities(self):
    WinePersonality.objects.get_or_create(name="Easy Going",
                                  description="You're \"easy going\" - even before the \
                                  wine. You're the type of person that \
                                  comes home after a long day at the \
                                  office or with the kids and reaches for a \
                                  glass. Your wine is happy, light and \
                                  white - clean, eortless and something \
                                  to unwind with.")

    WinePersonality.objects.get_or_create(name="Moxie",
                                  description="Bold, confident, outstanding - and we're \
                                  talking about you as much as the wine you drink. You don't talk, you make a \
                                  statement - and when it's about wine, it's \"I \
                                  drink red!\". Dynamic and charismatic, you \
                                  could spend the night with just these \
                                  wines and be completely content.")

    WinePersonality.objects.get_or_create(name="Whimsical",
                                  description="You find comfort in the wine you drink - \
                                  wine for you is an occasion where you're \
                                  often the life of the party. Life's not that \
                                  complicated, nor is your wine. The key \
                                  for you is FUN. Some may consider you \
                                  a little quirky and frequently playful, and \
                                  that's what's in your glass.")

    WinePersonality.objects.get_or_create(name="Sensational",
                                  description="And that you are. You put thought into \
                                  your whole wine experience, thirsting for \
                                  everything in the glass - the history, the \
                                  depth, the pairings - all are appreciated in \
                                  every sip. The wines are exciting, \
                                  stunning, and entices you into exploring \
                                  even more.")

    WinePersonality.objects.get_or_create(name="Exuberant",
                                  description="Vivacious and cheerful, you're often the \
                                  host of the party. You see your wine as \
                                  an accompaniment both for the evening \
                                  or the food. But you do not necessarily \
                                  see it taking center stage. Your wine is a \
                                  lively yet informal addition, whose \
                                  absence would be missed.")

    WinePersonality.objects.get_or_create(name="Serendipitous",
                                  description="When asked do you prefer red or white? \
                                  You say YES! Often welcoming impromptu \
                                  opportunities with a desire for \
                                  spontaneity, chance and discovery of life \
                                  and wine. Your unconstrained nature \
                                  empowers you to float from one sensual \
                                  pleasure to the next.")

    WinePersonality.objects.get_or_create(name="Complex",
                                  description="You have a very complex taste palate. It will require more experimentation to understand your tastes.")

  def create_wine_samplers(self):

    Wine.objects.get_or_create(name="Domaine De Pellehaut \"Harmonie De Gascogne\"",
                        sip_bits="Light, \"clean\" blend of four regional varietals \
                            from the Loire Valley (France), predominantly Uni Blanc and Columbard.",
                        number=1,
                        active=True)
    Wine.objects.get_or_create(name="Contrada Chardonnay",
                        sip_bits="Classic California chard. Made by respected wine-maker Michael \
                                Pozzan.  This wine has limited availability and crated for the \
                                restaurant industry.",
                        number=2,
                        active=True)
    Wine.objects.get_or_create(name="Foris Vineyards Muscat Frizzante",
                        sip_bits="This wine defines \"aromatics on the nose\"; \"Frizzante\" is \
                            Italian that refers to the slight effervescence, paying homage to this \
                            varietal's roots, although this wine hails from Oregon.", 
                        number=3,
                        active=True)
    Wine.objects.get_or_create(name="Giuseppe Savine Rondineto \"Vino Quotidinao\"",
                        sip_bits="Light bodied Italian red that can be served slight chilled (really) \
                            perfect for people just getting into the \"world of red\"; \
                            translates to \"wine for everyday\"; believe it or not, this is \
                            mad from 100% Merlot!",
                        number=4,
                        active=True)
    Wine.objects.get_or_create(name="Lange Twins Zinfandel",
                        sip_bits="Small Produced, Classic for the style. Fantastic, respected family-owned \
                            operation from Lodi, California.",
                        number=5,
                        active=True)
    Wine.objects.get_or_create(name="Carlos Basso Dos Fincas Cabernet Sauvignon/Merlot",
                        sip_bits="Awesome wine from South America. This line is special and only 3000 \
                            cases of this wine is produced. Bold, dark - might stain your teeth purple \
                            for a while - grab a steak or some Roquefort Bleu!",
                        number=6,
                        active=True)

  def create_contact_reasons(self):
    reason = ContactReason.objects.get_or_create(reason="Interested in holding a party")
    reason = ContactReason.objects.get_or_create(reason="Interested in becoming a party specialist")
    reason = ContactReason.objects.get_or_create(reason="Interested in attending a party in my local area")
    reason = ContactReason.objects.get_or_create(reason="Interested in finding more about Winedora")
    reason = ContactReason.objects.get_or_create(reason="Send me any new updates")
    reason = ContactReason.objects.get_or_create(reason="Other")

  def create_products(self):
    if Product.objects.all().count() < 4:
      f = open("data/tasting-kit.jpg", 'r')
      p, created = Product.objects.get_or_create(name="Host Tasting Kit",
                                    description="Host a party or understand your tastes",
                                    unit_price=125.00,
                                    category=Product.PRODUCT_TYPE[0][0],
                                    cart_tag="tasting_kit")
      self.assertEqual(created, True)
      p.image = File(f)
      p.save()
      f.close()


      f = open("data/SP_basic_prodimg.png", 'r')
      p, created = Product.objects.get_or_create(name="Basic Vinely Recommendation",
                                    description="Good set of wines for good people",
                                    unit_price=75.00,
                                    category=Product.PRODUCT_TYPE[1][0],
                                    cart_tag="basic")
      p.image = File(f)
      p.save()
      f.close()

      f = open("data/SP_classic_prodimg.png", 'r')
      p, created = Product.objects.get_or_create(name="Classic Vinely Recommendation",
                                    description="Better set of wines for better people",
                                    unit_price=120.00,
                                    category=Product.PRODUCT_TYPE[1][0],
                                    cart_tag="classic")
      p.image = File(f)
      p.save()
      f.close()

      f = open("data/SP_divine_prodimg.png", 'r')
      p, created = Product.objects.get_or_create(name="Divine Vinely Recommendation",
                                    description="Best set of wines for best people",
                                    unit_price=225.00,
                                    category=Product.PRODUCT_TYPE[1][0],
                                    cart_tag="divine")
      p.image = File(f)
      p.save()
      f.close()

  def setUp(self):
    # initial data
    #self.create_contact_reasons()

    # accounts are loaded from account/fixtures/initial_data.yaml
    #self.create_usable_accounts()
    #self.create_wine_personalities()
    #self.create_wine_samplers()
    self.create_products()

  def test_contact_us_models(self):
    total_reasons = ContactReason.objects.all().count()

    rand_ind = random.randint(1, total_reasons)
    reason = ContactReason.objects.get(id=rand_ind)
    req = ContactRequest(subject=reason, first_name="abc", last_name="def", email="hello@mit.edu", message="", zipcode="02139")
    req.save()

    rand_ind = random.randint(1, total_reasons)
    reason = ContactReason.objects.get(id=rand_ind)
    req = ContactRequest(subject=reason, first_name="abc", last_name="def", email="hello2@mit.edu", message="", zipcode="02139")
    req.save()

    rand_ind = random.randint(1, total_reasons)
    reason = ContactReason.objects.get(id=rand_ind)
    req = ContactRequest(subject=reason, first_name="abc", last_name="def", email="hello3@mit.edu", message="", zipcode="02139")
    req.save()

    rand_ind = random.randint(1, total_reasons)
    reason = ContactReason.objects.get(id=rand_ind)
    req = ContactRequest(subject=reason, first_name="abc", last_name="def", email="hello4@mit.edu", zipcode="02139")
    req.save()


  def test_party_creation_invitations(self):

    host1 = User.objects.get(email="host1@example.com")
    address1 = Address.objects.create(street1="65 Gordon St.",
                                      city="Detroit",
                                      state="MI",
                                      zipcode="42524-2342"
                                      )

    party1 = Party.objects.create(socializer=host1, title="John's party", description="Wine party on a sizzling hot day",
                              address=address1, event_date=datetime.today()+timedelta(days=10))

    host2 = User.objects.get(email="host2@example.com")
    address2 = Address.objects.create(nick_name="home address", 
                                      street1="65 Gordon St.",
                                      city="Detroit",
                                      state="MI",
                                      zipcode="42524-2342"
                                      )

    party2 = Party.objects.create(socializer=host2, title="Mary's party", description="Wine party in the garden",
                              address=address2, event_date=datetime.today()+timedelta(days=15))

    # invite people
    attendees1 = ['attendee1@example.com',
                  'attendee2@example.com',
                  'attendee3@example.com',
                  'attendee4@example.com',
                  'attendee5@example.com']


    attendees2 = ['attendee6@example.com',
                  'attendee7@example.com',
                  'attendee8@example.com',
                  'attendee9@example.com']


    for att in attendees1:
      PartyInvite.objects.create(party=party1, invitee=User.objects.get(email=att))

    for att in attendees2:
      PartyInvite.objects.create(party=party2, invitee=User.objects.get(email=att))

    # add and remove attendee
    cancelled = PartyInvite.objects.get(invitee=User.objects.get(email=attendees1[0]))
    cancelled.delete()

    PartyInvite.objects.create(party=party2, invitee=User.objects.get(email=attendees1[0]))

  def test_rep_adding_ratings(self):

    # login with rep
    response = self.client.login(email='specialist1@example.com', password='hello')

    #for g in Group.objects.all():
    #  print g.name

    self.assertEquals(Group.objects.all().count(), 4)

    ps_group = Group.objects.get(name="Vinely Pro")
    pro = User.objects.get(email='specialist1@example.com')
    self.assertEquals(ps_group in pro.groups.all(), True)

    response = self.client.get(reverse('main.views.record_wine_ratings'))
    self.assertEquals(response.status_code, 200)

    response = self.client.get(reverse('main.views.record_all_wine_ratings'))
    self.assertEquals(response.status_code, 200)

    # add an attendee information
    # type in the rating information
    response = self.client.post(reverse('main.views.record_all_wine_ratings'), {'first_name': 'Jane',
                                                        'last_name': 'Lamb',
                                                        'email': 'attendee1@example.com',
                                                        'wine1': 1,
                                                        'wine1_overall': 3,
                                                        'wine1_sweet': 4,
                                                        'wine1_sweet_dnl': 1,
                                                        'wine1_weight': 5,
                                                        'wine1_weight_dnl': 3,
                                                        'wine1_texture': 2,
                                                        'wine1_texture_dnl': 2,
                                                        'wine1_sizzle': 5,
                                                        'wine1_sizzle_dnl': 3,
                                                        'wine2': 2,
                                                        'wine2_overall': 4,
                                                        'wine2_sweet': 2,
                                                        'wine2_sweet_dnl': 3,
                                                        'wine2_weight': 5,
                                                        'wine2_weight_dnl': 2,
                                                        'wine2_texture': 5,
                                                        'wine2_texture_dnl': 1,
                                                        'wine2_sizzle': 3,
                                                        'wine2_sizzle_dnl': 1,
                                                        'wine3': 3,
                                                        'wine3_overall': 3,
                                                        'wine3_sweet': 4,
                                                        'wine3_sweet_dnl': 1,
                                                        'wine3_weight': 2,
                                                        'wine3_weight_dnl': 3,
                                                        'wine3_texture': 4,
                                                        'wine3_texture_dnl': 2,
                                                        'wine3_sizzle': 5,
                                                        'wine3_sizzle_dnl': 1,
                                                        'wine4': 4,
                                                        'wine4_overall': 4,
                                                        'wine4_sweet': 1,
                                                        'wine4_sweet_dnl': 3,
                                                        'wine4_weight': 2,
                                                        'wine4_weight_dnl': 3,
                                                        'wine4_texture': 5,
                                                        'wine4_texture_dnl': 3,
                                                        'wine4_sizzle': 4,
                                                        'wine4_sizzle_dnl': 3,
                                                        'wine5': 5,
                                                        'wine5_overall': 5,
                                                        'wine5_sweet': 4,
                                                        'wine5_sweet_dnl': 3,
                                                        'wine5_weight': 2,
                                                        'wine5_weight_dnl': 3,
                                                        'wine5_texture': 4,
                                                        'wine5_texture_dnl': 3,
                                                        'wine5_sizzle': 4,
                                                        'wine5_sizzle_dnl': 2,
                                                        'wine6': 6,
                                                        'wine6_overall': 4,
                                                        'wine6_sweet': 5,
                                                        'wine6_sweet_dnl': 2,
                                                        'wine6_weight': 3,
                                                        'wine6_weight_dnl': 2,
                                                        'wine6_texture': 4,
                                                        'wine6_texture_dnl': 2,
                                                        'wine6_sizzle': 5,
                                                        'wine6_sizzle_dnl': 1
                                                    })

    self.assertContains(response, "Here's your Wine Personality")

    self.client.login(email='attendee1@example.com', password='hello')

    user = User.objects.get(email="attendee1@example.com")

    response = self.client.post(reverse('main.views.record_wine_ratings'), {
                                                        'user': user.id,
                                                        'wine': 5,
                                                        'overall': 5,
                                                        'dnl': 3,
                                                        'sweet': 4,
                                                        'sweet_dnl': 3,
                                                        'weight': 2,
                                                        'weight_dnl': 3,
                                                        'texture': 4,
                                                        'texture_dnl': 3,
                                                        'sizzle': 4,
                                                        'sizzle_dnl': 2,

      })

    self.assertContains(response, "Here's your Wine Personality")

    # save and move to next attendee, may also order wines instead of going to next attendee

  def test_rep_adding_orders(self):
    pass

  def test_attendee_ordering_online(self):
    pass

  def test_supplier_viewing_fulfilling(self):
    pass

  def test_attendee_rating_order(self):
    pass

  def test_party_add_request(self):
    """
      1. Test party adding by specialist

      2. Test party add by host

      3. Test party add by attendee

    """

  def test_product_ordering(self):

    response = self.client.get(reverse("main.views.cart_add_tasting_kit"))

    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("main.views.cart_add_tasting_kit"), { "product": 1,
                                                                              "quantity": 2,
                                                                              "price_category": 0,
                                                                              "frequency": 0,
                                                                              "total_price": 100})
    self.assertRedirects(response, reverse("main.views.cart"))

  def test_basic_addition(self):
    """
    Tests that 1 + 1 always equals 2.
    """
    self.assertEqual(1 + 1, 2)
