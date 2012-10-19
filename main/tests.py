"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.core.files import File
from accounts.models import Address, Zipcode

from main.models import ContactReason, ContactRequest, Party, PartyInvite, Product, LineItem, Order
from personality.models import Wine, WinePersonality
from emailusernames.utils import create_user, create_superuser

import random
from datetime import date, datetime, timedelta
from django.utils import timezone
from cms.tests import SimpleTest as CMSTest
from support.models import Email

class SimpleTest(TestCase):
  
  def runTest(self):
    pass

  def create_usable_accounts(self):
    """
      create usable accounts
    """
    ps_group, created = Group.objects.get_or_create(name="Vinely Pro")
    ph_group, created = Group.objects.get_or_create(name="Vinely Host")
    att_group, created = Group.objects.get_or_create(name="Vinely Taster")
    supp_group, created = Group.objects.get_or_create(name="Supplier")
    pending_pro_group, created = Group.objects.get_or_create(name="Pending Vinely Pro")

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

    Zipcode.objects.get_or_create(code="02139", country="US", state="MA")
    Zipcode.objects.get_or_create(code="42524", country="US", state="MI")
    Zipcode.objects.get_or_create(code="60107", country="US", state="CA")

    for u in User.objects.all():
      u.is_active = True
      u.save()

  # def test_admin_actions(self):
  #   response = self.client.login(email="attendee2@example.com", password="hello")
  #   self.assertEquals(response, True)

  #   admin = User.objects.get(email="specialist1@example.com")
  #   pro = User.objects.get(email="specialist2@example.com")

  #   response = self.client.post('/admin/main/myhost/', {'action':})
  #   self.assertContains(response, "New pro has been successfully assigned.")


  def create_wine_personalities(self):
    WinePersonality.objects.get_or_create(name="Easy Going",
                                  headline="You're \"easygoing,\" even before the wine.",
                                  description="You're the type of person who comes home after a long day and reaches \
                                   for a glass. Your wine is happy, light, and white - clean, effortless, and something \
                                   to unwind with. It's easy for you to relax and escape, especially with a glass in hand.")

    WinePersonality.objects.get_or_create(name="Moxie",
                                  headline="Bold, confident, outstanding.",
                                  description="We're talking about you as much as the wine you drink. You don't talk, \
                                    you make a statement - and when it's about wine, it's \"I drink red!\" Dynamic \
                                    and charismatic, you could spend the night with just these wines and be completely content.")

    WinePersonality.objects.get_or_create(name="Whimsical",
                                  headline="You find comfort in the wine you drink.",
                                  description="Wine for you is an occasion where you're often the life of the party. \
                                   Life's not that complicated, nor is your wine. The key for you is FUN. Some may \
                                   consider you a little quirky and frequently playful, and that's what's in your glass.")

    WinePersonality.objects.get_or_create(name="Sensational",
                                  headline="And that you are.",
                                  description="You put thought into your whole wine experience, thirsting for everything in the glass \
                                    - the history, the depth, the pairings - all are appreciated in every sip. The wines are exciting, \
                                    stunning, and entice you into exploring even more.")

    WinePersonality.objects.get_or_create(name="Exuberant",
                                  headline="Vivacious and cheerful, you're often the host.",
                                  description="You see your wine as an accompaniment - for the evening or the food. \
                                    But you do not necessarily see it taking center stage. Your wine is a lively yet \
                                    informal addition, one whose absence would be missed.")

    WinePersonality.objects.get_or_create(name="Serendipitous",
                                  headline="When asked if you prefer red or white, you say, \"YES!\"",
                                  description="You welcome impromptu opportunities with open arms. Your greatest joy is \
                                  making surprising discoveries in your life - and your wine. Your unconstrained nature \
                                  empowers you to float from one sensual pleasure to the next.")

    WinePersonality.objects.get_or_create(name="Mystery",
                                  headline="You follow every clue.",
                                  description="You're full of personality. So which one is it? Are you Whimsical? Serendipitous? \
                                  Do you think you're Sensational? Exuberant? Full of Moxie or Easygoing? As soon as you find out, \
                                  great things will be there for the tasting!")

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
    reason = ContactReason.objects.get_or_create(reason="Interested in hosting a party in my local area")
    reason = ContactReason.objects.get_or_create(reason="Interested in becoming a Vinely Pro")
    reason = ContactReason.objects.get_or_create(reason="Interested in attending a party in my local area")
    reason = ContactReason.objects.get_or_create(reason="Interested in finding more about Vinely")
    reason = ContactReason.objects.get_or_create(reason="Send me any new updates")
    reason = ContactReason.objects.get_or_create(reason="Other")

  def create_products(self):
    """
      Need to specify pk explicitly or else it creates products with ID's that are incremental from previous entries
    """
    if Product.objects.all().count() < 6:
      f = open("data/firsthostkit_prodimg.png", 'r')
      p, created = Product.objects.get_or_create(pk=1, name="Vinely's First Taste Kit",
                                    description="<p>This is the official Vinely First Taste Kit that will help Vinely Tasters \
                                        discover their true wine personality. Included are six carefully-selected wines, offered \
                                        in three unique tasting experiences.</p>\
                                        <p>Choose the Basic First Taste Kit ($75) and get great tastes without a great investment. \
                                            Take your Tasters to exciting new places with the Superior First Taste Kit ($120). Or, \
                                            provide an unmatched, unforgettable experience with the Divine First Taste Kit ($225).</p>\
                                        <p>Each kit will reveal each Taster's personality. The only difference is in the quality of wine.\
                                            You know who you invited! Select based on their taste or yours.</p>",
                                    unit_price=75.00,
                                    category=Product.PRODUCT_TYPE[0][0],
                                    cart_tag="tasting_kit")
      self.assertEqual(created, True)
      p.image = File(f)
      p.save()
      f.close()

      #f = open("data/firsthostkit_prodimg.png", 'r')
      p, created = Product.objects.get_or_create(pk=2, name="Vinely's Superior Taste Kit",
                                    description="<p>This is the official Vinely First Taste Kit that will help Vinely Tasters \
                                        discover their true wine personality. Included are six carefully-selected wines, offered \
                                        in three unique tasting experiences.</p>\
                                        <p>Choose the Basic First Taste Kit ($75) and get great tastes without a great investment. \
                                            Take your Tasters to exciting new places with the Superior First Taste Kit ($120). Or, \
                                            provide an unmatched, unforgettable experience with the Divine First Taste Kit ($225).</p>\
                                        <p>Each kit will reveal each Taster's personality. The only difference is in the quality of wine.\
                                            You know who you invited! Select based on their taste or yours.</p>",
                                    unit_price=120.00,
                                    category=Product.PRODUCT_TYPE[0][0],
                                    cart_tag="tasting_kit")
      self.assertEqual(created, True)
      #p.image = File(f)
      p.save()
      #f.close()

      #f = open("data/firsthostkit_prodimg.png", 'r')
      p, created = Product.objects.get_or_create(pk=3, name="Vinely's Divine Taste Kit",
                                    description="<p>This is the official Vinely First Taste Kit that will help Vinely Tasters \
                                        discover their true wine personality. Included are six carefully-selected wines, offered \
                                        in three unique tasting experiences.</p>\
                                        <p>Choose the Basic First Taste Kit ($75) and get great tastes without a great investment. \
                                            Take your Tasters to exciting new places with the Superior First Taste Kit ($120). Or, \
                                            provide an unmatched, unforgettable experience with the Divine First Taste Kit ($225).</p>\
                                        <p>Each kit will reveal each Taster's personality. The only difference is in the quality of wine.\
                                            You know who you invited! Select based on their taste or yours.</p>",
                                    unit_price=225.00,
                                    category=Product.PRODUCT_TYPE[0][0],
                                    cart_tag="tasting_kit")
      self.assertEqual(created, True)
      #p.image = File(f)
      p.save()
      #f.close()


      f = open("data/SP_basic_prodimg.png", 'r')
      p, created = Product.objects.get_or_create(pk=4, name="Basic Collection",
                                    description="The {{ personality }} Basic Collection is lively, yet \
                                    laid-back - just like life should be. It offers a dynamic medley \
                                    of flavors you won't be able to resist. For those new to the world \
                                    of wine, it provides great taste without requiring a great investment.",
                                    unit_price=75.00,
                                    full_case_price=140.00,
                                    category=Product.PRODUCT_TYPE[1][0],
                                    cart_tag="basic")
      p.image = File(f)
      p.save()
      f.close()

      f = open("data/SP_superior_prodimg.png", 'r')
      p, created = Product.objects.get_or_create(pk=5, name="Superior Collection",
                                    description="Great for enjoying alone or with friends, each \
                                    bottle is filled with the potential to take your wine experience \
                                    to exciting new places. The {{personality}} Superior Collection \
                                    is the perfect choice for those with a passion for wine and its \
                                    ability to enhance any mood or setting.",
                                    unit_price=120.00,
                                    full_case_price=220.00,
                                    category=Product.PRODUCT_TYPE[1][0],
                                    cart_tag="superior")
      p.image = File(f)
      p.save()
      f.close()

      f = open("data/SP_divine_prodimg.png", 'r')
      p, created = Product.objects.get_or_create(pk=6, name="Divine Collection",
                                    description="Captivating. Balanced. Brilliant. You're full \
                                    of depth and so is the {{personality}} Divine Collection. \
                                    Excite your senses each and every time you pour a glass. \
                                    The unmatched experience each bottle provides will have you \
                                    appreciating every sip, every scent, and every penny paid.",
                                    unit_price=225.00,
                                    full_case_price=420.00,
                                    category=Product.PRODUCT_TYPE[1][0],
                                    cart_tag="divine")
      p.image = File(f)
      p.save()
      f.close()

  def setUp(self):
    # initial data
    #self.create_contact_reasons()

    # accounts are loaded from account/fixtures/initial_data.yaml
    self.create_usable_accounts()
    #self.create_wine_personalities()
    #self.create_wine_samplers()
    self.create_products()
    test = CMSTest()
    test.create_email_templates()


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

    party1 = Party.objects.create(host=host1, title="John's party", description="Wine party on a sizzling hot day",
                              address=address1, event_date=timezone.now()+timedelta(days=10))

    host2 = User.objects.get(email="host2@example.com")
    address2 = Address.objects.create(nick_name="home address", 
                                      street1="65 Gordon St.",
                                      city="Detroit",
                                      state="MI",
                                      zipcode="42524-2342"
                                      )

    party2 = Party.objects.create(host=host2, title="Mary's party", description="Wine party in the garden",
                              address=address2, event_date=timezone.now()+timedelta(days=15))

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

    self.assertEquals(Group.objects.all().count(), 5)

    ps_group = Group.objects.get(name="Vinely Pro")
    pro = User.objects.get(email='specialist1@example.com')
    self.assertEquals(ps_group in pro.groups.all(), True)

    response = self.client.get(reverse('personality.views.record_wine_ratings'))
    self.assertEquals(response.status_code, 200)

    response = self.client.get(reverse('personality.views.record_all_wine_ratings'))
    self.assertEquals(response.status_code, 200)

    # add an attendee information
    # type in the rating information
    response = self.client.post(reverse('personality.views.record_all_wine_ratings'), {'first_name': 'Jane',
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
    
    self.assertContains(response, "you are a Serendipitous")

    self.client.login(email='attendee1@example.com', password='hello')

    user = User.objects.get(email="attendee1@example.com")

    response = self.client.post(reverse('personality.views.record_wine_ratings'), {
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

  def create_party(self):
    host1 = User.objects.get(email="host1@example.com")
    address1 = Address.objects.create(street1="65 Gordon St.",
                                      city="Detroit",
                                      state="MI",
                                      zipcode="42524-2342"
                                      )

    party = Party.objects.create(host=host1, title="John's party", description="Wine party on a sizzling hot day",
                              address=address1, event_date=timezone.now()+timedelta(days=10))
    # invite people
    attendees1 = ['attendee1@example.com',
                  'attendee2@example.com',
                  'attendee3@example.com',
                  'attendee4@example.com',
                  'attendee5@example.com']

    for att in attendees1:
      PartyInvite.objects.create(party=party, invitee=User.objects.get(email=att))

    return party

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
    party = self.create_party()

    response = self.client.login(email="host1@example.com", password="hello")
    self.assertTrue(response)

    response = self.client.get(reverse("main.views.cart_add_tasting_kit", args=[party.id]))

    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("main.views.cart_add_tasting_kit", args=[party.id]), { "product": 100,
                                                                              "quantity": 2,
                                                                              "price_category": 0,
                                                                              "frequency": 0,
                                                                              "total_price": 100})
    self.assertContains(response, "Select a valid choice.")

    kit = Product.objects.get(name="Vinely's First Taste Kit", unit_price=75.00)

    response = self.client.post(reverse("main.views.cart_add_tasting_kit", args=[party.id]), { "product": kit.id,
                                                                              "quantity": 2,
                                                                              "price_category": 0,
                                                                              "frequency": 0,
                                                                              "total_price": 140.00})
    self.assertRedirects(response, reverse("main.views.cart"))

    party2 = self.create_party()
    
    response = self.client.get(reverse("main.views.cart_add_tasting_kit", args=[party2.id]))
    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("main.views.cart_add_tasting_kit", args=[party2.id]), { "product": kit.id,
                                                                              "quantity": 2,
                                                                              "price_category": 0,
                                                                              "frequency": 0,
                                                                              "total_price": 140.00})
    # redirects to same page with error message
    self.assertRedirects(response, reverse("main.views.cart_add_tasting_kit", args=[party2.id]))
    # self.assertContains(response, "You can only order taste kits for one party at a time.")
    
    case = Product.objects.get(name="Vinely's Superior Taste Kit", unit_price=120.00)
    response = self.client.post(reverse("main.views.cart_add_wine", args=["superior"]), { "product": case.id,
                                                                              "quantity": 2,
                                                                              # "price_category": 0,
                                                                              "frequency": 0,
                                                                              "total_price": 240.00,
                                                                              "level": "superior"})
    # redirects to same page with error message
    self.assertRedirects(response, reverse("main.views.cart_add_wine", args=["superior"]))
    # self.assertContains(response, 'A tasting kit is already in your cart')

    response = self.client.get(reverse("main.views.edit_shipping_address"))
    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("main.views.edit_shipping_address"), { "first_name": "John",
                                                                        "last_name": "Doe",
                                                                        "address1": "65 Gordon St.",
                                                                        "city": "Cambridge",
                                                                        "state": "MA",
                                                                        "zipcode": "02139",
                                                                        "phone": "555-617-6706",
                                                                        "email": "host1@example.com"})
    self.assertContains(response, "You MUST be over 21 to make an order")

    user = User.objects.get(email="host1@example.com")
    profile = user.get_profile()
    profile.dob = timezone.now() - timedelta(days = 30*365)
    profile.save()

    # check switch between stripe and vinely credit cards
    response = self.client.post(reverse("main.views.edit_shipping_address"), { "first_name": "John",
                                                                        "last_name": "Doe",
                                                                        "address1": "65 Gordon St.",
                                                                        "city": "Detroit",
                                                                        "state": "MI",
                                                                        "zipcode": "42524",
                                                                        "phone": "555-617-6706",
                                                                        "email": "host1@example.com"})
    self.assertRedirects(response, reverse("main.views.edit_credit_card"))

    response = self.client.get(reverse("main.views.edit_credit_card"))
    self.assertContains(response, "Stripe.setPublishableKey")

    # check zipcode supported
    response = self.client.post(reverse("main.views.edit_shipping_address"), { "first_name": "John",
                                                                        "last_name": "Doe",
                                                                        "address1": "65 Gordon St.",
                                                                        "city": "Cambridge",
                                                                        "state": "MA",
                                                                        "zipcode": "10016",
                                                                        "phone": "555-617-6706",
                                                                        "email": "host1@example.com"})
    self.assertContains(response, "Vinely does not currently operate in the specified area")

    response = self.client.post(reverse("main.views.edit_shipping_address"), { "first_name": "John",
                                                                        "last_name": "Doe",
                                                                        "address1": "65 Gordon St.",
                                                                        "city": "Cambridge",
                                                                        "state": "MA",
                                                                        "zipcode": "02139",
                                                                        "phone": "555-617-6706",
                                                                        "email": "host1@example.com"})
    self.assertRedirects(response, reverse("main.views.edit_credit_card"))

    # check if new user created
    response = self.client.post(reverse("main.views.edit_shipping_address"), { "first_name": "John",
                                                                        "last_name": "Doe",
                                                                        "address1": "65 Gordon St.",
                                                                        "city": "Cambridge",
                                                                        "state": "MA",
                                                                        "zipcode": "02139",
                                                                        "phone": "555-617-6706",
                                                                        "email": "buyer@example.com"})
    self.assertTrue(User.objects.filter(email="buyer@example.com").exists())
    self.assertRedirects(response, reverse("main.views.edit_credit_card"))

    year = datetime.today().year + 5
    response = self.client.post(reverse("main.views.edit_credit_card"), { "card_number": "4111111111111",
                                                                        "exp_month": 6,
                                                                        "exp_year": year,
                                                                        "verification_code": 111,
                                                                        "billing_zipcode": "02139",
                                                                        "card_type": "Unknown" })
    self.assertRedirects(response, reverse("main.views.place_order"))

    response = self.client.post(reverse("main.views.place_order"))
    order = Order.objects.get(cart__items__product = kit)

    self.assertRedirects(response, reverse("main.views.order_complete", args=[order.order_id]))
    
    # check emails sent
    recipient_email = Email.objects.filter(subject="Your Vinely order was placed successfully!", recipients="[u'buyer@example.com']")
    self.assertTrue(recipient_email.exists())

    subject = "Order ID: %s has been submitted!" % order.order_id
    vinely_email = Email.objects.filter(subject=subject, recipients="['fulfillment@vinely.com']")

    # self.assertRedirects(response, reverse("main.views.order_complete", args=[]))
    self.client.logout()

    ######################################################################################
    #
    # case orders flow from here
    #
    ######################################################################################

    response = self.client.login(email="host1@example.com", password="hello")
    self.assertTrue(response)

    response = self.client.get(reverse("main.views.cart_add_wine", args=["superior"]))

    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("main.views.cart_add_wine", args=["superior"]), { "product": case.id,
                                                                                          "quantity": 2,
                                                                                          "frequency": 0,
                                                                                          "total_price": 220.00,
                                                                                          "level": "superior"})
    self.assertRedirects(response, reverse("main.views.cart"))

    response = self.client.get(reverse("main.views.customize_checkout"))
    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("main.views.customize_checkout"), { "product": case.id,
                                                                            "wine_mix": 1,
                                                                            "sparkling": 0})
    self.assertRedirects(response, reverse("main.views.edit_shipping_address"))

    response = self.client.post(reverse("main.views.edit_shipping_address"), { "first_name": "John",
                                                                        "last_name": "Doe",
                                                                        "address1": "65 Gordon St.",
                                                                        "city": "Cambridge",
                                                                        "state": "MA",
                                                                        "zipcode": "02139",
                                                                        "phone": "555-617-6706",
                                                                        "email": "host1@example.com"})
    self.assertRedirects(response, reverse("main.views.edit_credit_card"))

    year = datetime.today().year + 5
    response = self.client.post(reverse("main.views.edit_credit_card"), { "card_number": "4111111111111",
                                                                        "exp_month": 6,
                                                                        "exp_year": year,
                                                                        "verification_code": 111,
                                                                        "billing_zipcode": "02139",
                                                                        "card_type": "Unknown" })
    self.assertRedirects(response, reverse("main.views.place_order"))
    
    response = self.client.post(reverse("main.views.place_order"))
    order = Order.objects.get(cart__items__product = case)

    self.assertRedirects(response, reverse("main.views.order_complete", args=[order.order_id]))
    
    self.assertTrue(Order.objects.filter(cart__items__product = case).exists())
    
    # check emails sent
    recipient_email = Email.objects.filter(subject="Your Vinely order was placed successfully!", recipients="[u'host1@example.com']")
    self.assertTrue(recipient_email.exists())
    subject = "Order ID: %s has been submitted!" % order.order_id
    vinely_email = Email.objects.filter(subject=subject, recipients="['fulfillment@vinely.com']")
    # self.client.logout()

    # TODO: Pro order for taster

  def test_basic_addition(self):
    """
    Tests that 1 + 1 always equals 2.
    """
    self.assertEqual(1 + 1, 2)
