"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.files import File
from accounts.models import Address, Zipcode, UserProfile

from main.models import ContactReason, ContactRequest, Party, PartyInvite, Product, Order, OrganizedParty, MyHost, \
                        InvitationSent
from personality.models import Wine, WinePersonality
from emailusernames.utils import create_user

import random
from datetime import datetime, timedelta
from django.utils import timezone
from cms.tests import SimpleTest as CMSTest
from support.models import Email
import unittest


class SimpleTest(TestCase):

  def runTest(self):
    pass

  def create_usable_accounts(self):
    """
      create usable accounts
    """
    ps_group = UserProfile.ROLE_CHOICES[1][0]
    ph_group = UserProfile.ROLE_CHOICES[2][0]
    att_group = UserProfile.ROLE_CHOICES[3][0]
    supp_group = UserProfile.ROLE_CHOICES[4][0]
    pending_pro_group = UserProfile.ROLE_CHOICES[5][0]

    Zipcode.objects.get_or_create(code="02139", country="US", state="MA")
    Zipcode.objects.get_or_create(code="49546", country="US", state="MI")
    Zipcode.objects.get_or_create(code="92612", country="US", state="CA")

    mi_pro = create_user("elizabeth@vinely.com", "egoede")
    mi_pro.is_staff = True
    mi_pro.is_superuser = True
    mi_pro.save()
    mi_pro.userprofile.role = ps_group
    mi_pro.userprofile.zipcode = '49546'
    mi_pro.userprofile.save()

    sales_user = create_user('getstarted@vinely.com', 'hello')
    sales_user.first_name = "Vinely"
    sales_user.last_name = "Sales"
    sales_user.save()
    sales_user.userprofile.role = 0
    sales_user.userprofile.phone = '888-294-1128'
    sales_user.userprofile.save()

    care_user = create_user("care@vinely.com", "hello")
    care_user.first_name = "Vinely"
    care_user.last_name = "Care"
    care_user.is_active = False
    care_user.save()
    care_user.userprofile.role = 0  # no assigned role
    care_user.userprofile.phone = '888-294-1128'
    care_user.userprofile.save()

    ca_pro = create_user("johnstecco@gmail.com", "jstecco")
    ca_pro.userprofile.role = ps_group
    ca_pro.userprofile.zipcode = '92612'
    ca_pro.userprofile.save()

    ma_pro = create_user("specialist1@example.com", "hello")
    ma_pro.userprofile.role = ps_group
    ma_pro.userprofile.zipcode = '02139'
    ma_pro.userprofile.save()

    u = create_user("specialist2@example.com", "hello")
    u.userprofile.role = ps_group
    u.userprofile.save()

    u = create_user("host1@example.com", "hello")
    u.userprofile.role = ph_group
    u.userprofile.save()

    u = create_user("host2@example.com", "hello")
    u.userprofile.role = ph_group
    u.userprofile.save()

    u = create_user("host3@example.com", "hello")
    u.userprofile.role = ph_group
    u.userprofile.save()

    u = create_user("attendee1@example.com", "hello")
    u.userprofile.role = att_group
    u.userprofile.save()

    u = create_user("attendee2@example.com", "hello")
    u.userprofile.role = att_group
    u.userprofile.save()

    u = create_user("attendee3@example.com", "hello")
    u.userprofile.role = att_group
    u.userprofile.save()

    u = create_user("attendee4@example.com", "hello")
    u.userprofile.role = att_group
    u.userprofile.save()

    u = create_user("attendee5@example.com", "hello")
    u.userprofile.role = att_group
    u.userprofile.save()

    u = create_user("attendee6@example.com", "hello")
    u.userprofile.role = att_group
    u.userprofile.save()

    u = create_user("attendee7@example.com", "hello")
    u.userprofile.role = att_group
    u.userprofile.save()

    u = create_user("attendee8@example.com", "hello")
    u.userprofile.role = att_group
    u.userprofile.save()

    u = create_user("attendee9@example.com", "hello")
    u.userprofile.role = att_group
    u.userprofile.save()

    u = create_user("supplier1@example.com", "hello")
    u.userprofile.role = supp_group
    u.userprofile.save()

    u = create_user("supplier2@example.com", "hello")
    u.userprofile.role = supp_group
    u.userprofile.save()

    suppliers = User.objects.filter(userprofile__role=supp_group)
    self.assertEqual(suppliers.count(), 2)

    tasters = User.objects.filter(userprofile__role=att_group)
    self.assertEqual(tasters.count(), 9)

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
    WinePersonality.objects.get_or_create(pk=1, name="Easy Going",
                                  headline="You're \"easygoing,\" even before the wine.",
                                  description="You're the type of person who comes home after a long day and reaches \
                                   for a glass. Your wine is happy, light, and white - clean, effortless, and something \
                                   to unwind with. It's easy for you to relax and escape, especially with a glass in hand.")

    WinePersonality.objects.get_or_create(pk=2, name="Moxie",
                                  headline="Bold, confident, outstanding.",
                                  description="We're talking about you as much as the wine you drink. You don't talk, \
                                    you make a statement - and when it's about wine, it's \"I drink red!\" Dynamic \
                                    and charismatic, you could spend the night with just these wines and be completely content.")

    WinePersonality.objects.get_or_create(pk=3, name="Whimsical",
                                  headline="You find comfort in the wine you drink.",
                                  description="Wine for you is an occasion where you're often the life of the party. \
                                   Life's not that complicated, nor is your wine. The key for you is FUN. Some may \
                                   consider you a little quirky and frequently playful, and that's what's in your glass.")

    WinePersonality.objects.get_or_create(pk=4, name="Sensational",
                                  headline="And that you are.",
                                  description="You put thought into your whole wine experience, thirsting for everything in the glass \
                                    - the history, the depth, the pairings - all are appreciated in every sip. The wines are exciting, \
                                    stunning, and entice you into exploring even more.")

    WinePersonality.objects.get_or_create(pk=5, name="Exuberant",
                                  headline="Vivacious and cheerful, you're often the host.",
                                  description="You see your wine as an accompaniment - for the evening or the food. \
                                    But you do not necessarily see it taking center stage. Your wine is a lively yet \
                                    informal addition, one whose absence would be missed.")

    WinePersonality.objects.get_or_create(pk=6, name="Serendipitous",
                                  headline="When asked if you prefer red or white, you say, \"YES!\"",
                                  description="You welcome impromptu opportunities with open arms. Your greatest joy is \
                                  making surprising discoveries in your life - and your wine. Your unconstrained nature \
                                  empowers you to float from one sensual pleasure to the next.")

    WinePersonality.objects.get_or_create(pk=7, name="Mystery",
                                  headline="You follow every clue.",
                                  description="You're full of personality. So which one is it? Are you Whimsical? Serendipitous? \
                                  Do you think you're Sensational? Exuberant? Full of Moxie or Easygoing? As soon as you find out, \
                                  great things will be there for the tasting!")

  def create_wine_samplers(self):

    Wine.objects.get_or_create(pk=1, name="Domaine De Pellehaut \"Harmonie De Gascogne\"",
                        sip_bits="Light, \"clean\" blend of four regional varietals \
                            from the Loire Valley (France), predominantly Uni Blanc and Columbard.",
                        number=1,
                        active=True)
    Wine.objects.get_or_create(pk=2, name="Contrada Chardonnay",
                        sip_bits="Classic California chard. Made by respected wine-maker Michael \
                                Pozzan.  This wine has limited availability and crated for the \
                                restaurant industry.",
                        number=2,
                        active=True)
    Wine.objects.get_or_create(pk=3, name="Foris Vineyards Muscat Frizzante",
                        sip_bits="This wine defines \"aromatics on the nose\"; \"Frizzante\" is \
                            Italian that refers to the slight effervescence, paying homage to this \
                            varietal's roots, although this wine hails from Oregon.",
                        number=3,
                        active=True)
    Wine.objects.get_or_create(pk=4, name="Giuseppe Savine Rondineto \"Vino Quotidinao\"",
                        sip_bits="Light bodied Italian red that can be served slight chilled (really) \
                            perfect for people just getting into the \"world of red\"; \
                            translates to \"wine for everyday\"; believe it or not, this is \
                            mad from 100% Merlot!",
                        number=4,
                        active=True)
    Wine.objects.get_or_create(pk=5, name="Lange Twins Zinfandel",
                        sip_bits="Small Produced, Classic for the style. Fantastic, respected family-owned \
                            operation from Lodi, California.",
                        number=5,
                        active=True)
    Wine.objects.get_or_create(pk=6, name="Carlos Basso Dos Fincas Cabernet Sauvignon/Merlot",
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

  def create_test_products(self):
    if Product.objects.all().count() < 4:
      p, created = Product.objects.get_or_create(name="3 Bottles", description="", unit_price=54.00, category=1, cart_tag="3")
      self.assertEqual(created, True)
      p, created = Product.objects.get_or_create(name="6 Bottles", description="", unit_price=97.00, category=1, cart_tag="6")
      self.assertEqual(created, True)
      p, created = Product.objects.get_or_create(name="12 Bottles", description="", unit_price=173.00, category=1, cart_tag="12")
      self.assertEqual(created, True)
      p, created = Product.objects.get_or_create(name="Vinely's First Taste Kit", description="", unit_price=99.00, category=0, cart_tag="12")
      self.assertEqual(created, True)

  def setUp(self):
    # initial data
    #self.create_contact_reasons()

    # accounts are loaded from account/fixtures/initial_data.yaml
    self.create_usable_accounts()
    self.create_wine_personalities()
    self.create_wine_samplers()
    self.create_test_products()
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

  # def old_test_invite_to_party(self):
  #   '''
  #   Test inviting people to party by host and invitee
  #   Invite by Pro covered in @test_rep_create_party
  #   '''
  #   party = self.create_party()

  #   ############################################
  #   # invites by host
  #   ############################################
  #   response = self.client.login(email='host1@example.com', password='hello')
  #   self.assertTrue(response)

  #   # invite existing tasters
  #   response = self.client.get(reverse('main.views.party_taster_invite'))
  #   self.assertEquals(response.status_code, 200)

  #   # select taster from list
  #   invitee = User.objects.get(email='attendee6@example.com')

  #   response = self.client.post(reverse('main.views.party_taster_invite'),  {'party': party.id,
  #                                                           'invitee': invitee.id})

  #   self.assertRedirects(response, reverse('main.views.party_details', args=[party.id]))

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='attendee6@example.com').exists())

  #   # enter existing user in form
  #   response = self.client.post(reverse('main.views.party_taster_invite'),  {'party': party.id,
  #                                                           'first_name': 'Attendee',
  #                                                           'last_name': 'Six',
  #                                                           'email': 'attendee7@example.com'})
  #   self.assertRedirects(response, reverse('main.views.party_details', args=[party.id]))

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='attendee7@example.com').exists())

  #   # invite new user
  #   response = self.client.post(reverse('main.views.party_taster_invite'),  {'party': party.id,
  #                                                           'first_name': 'New',
  #                                                           'last_name': 'Guy',
  #                                                           'email': 'new.guy@example.com'})
  #   self.assertRedirects(response, reverse('main.views.party_details', args=[party.id]))

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='new.guy@example.com').exists())

  #   # recipient_email = Email.objects.filter(subject__icontains="has invited you to a Vinely Party!", recipients="[u'new.guy@example.com']")
  #   # self.assertTrue(recipient_email.exists())

  #   self.client.logout()

  #   ############################################
  #   # Invites by taster
  #   ############################################
  #   response = self.client.login(email='attendee3@example.com', password='hello')
  #   self.assertTrue(response)

  #   # invite existing tasters
  #   response = self.client.get(reverse('main.views.party_taster_invite'))
  #   self.assertEquals(response.status_code, 200)

  #   # enter existing user in form
  #   response = self.client.post(reverse('main.views.party_taster_invite'),  {'party': party.id,
  #                                                           'first_name': 'Attendee',
  #                                                           'last_name': 'Eight',
  #                                                           'email': 'attendee8@example.com'})
  #   self.assertRedirects(response, reverse('main.views.party_details', args=[party.id]))

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='attendee8@example.com').exists())

  #   # invite new user
  #   response = self.client.post(reverse('main.views.party_taster_invite'),  {'party': party.id,
  #                                                           'first_name': 'New',
  #                                                           'last_name': 'Guy2',
  #                                                           'email': 'new.guy2@example.com'})
  #   self.assertRedirects(response, reverse('main.views.party_details', args=[party.id]))

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='new.guy2@example.com').exists())

    # recipient_email = Email.objects.filter(subject__icontains="invited you to a Vinely Party!", recipients="[u'new.guy2@example.com']")
    # self.assertTrue(recipient_email.exists())

    # TODO: Hit send invite and check if mails are sent
  # def test_invite_to_party_new_flow(self):
  #   '''
  #   Test inviting people to party by host and invitee
  #   Invite by Pro covered in @test_rep_create_party
  #   '''
  #   party = self.create_party()

  #   ############################################
  #   # invites by host
  #   ############################################
  #   response = self.client.login(email='host1@example.com', password='hello')
  #   self.assertTrue(response)

  #   # select taster from list
  #   invitee = User.objects.get(email='attendee6@example.com')
  #   response = self.client.post(reverse('party_details', args=[party.id]), {'party': party.id,
  #                                                             'invitee': invitee.id,
  #                                                             'add_taster': 'add_taster',
  #                                                             'response': 0})

  #   self.assertContains(response, "has been added to the party invitations list")

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee=invitee).exists())

  #   # enter existing user in form
  #   response = self.client.post(reverse('party_details', args=[party.id]), {'party': party.id,
  #                                                             'first_name': 'Attendee',
  #                                                             'last_name': 'Seven',
  #                                                             'email': 'attendee7@example.com',
  #                                                             'response': 0,
  #                                                             'add_taster': 'add_taster'})
  #   self.assertContains(response, "has been added to the party invitations list")

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='attendee7@example.com').exists())

  #   # invite new user
  #   response = self.client.post(reverse('party_details', args=[party.id]), {'party': party.id,
  #                                                             'first_name': 'New',
  #                                                             'last_name': 'Guy',
  #                                                             'email': 'new.guy@example.com',
  #                                                             'response': 0,
  #                                                             'add_taster': 'add_taster'})
  #   self.assertContains(response, "has been added to the party invitations list")

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='new.guy@example.com').exists())

  #   self.client.logout()

  #   ############################################
  #   # Invites by taster
  #   ############################################
  #   response = self.client.login(email='attendee3@example.com', password='hello')
  #   self.assertTrue(response)

  #   # enter existing user in form
  #   response = self.client.post(reverse('party_details', args=[party.id]), {'party': party.id,
  #                                                             'first_name': 'Attendee',
  #                                                             'last_name': 'Eight',
  #                                                             'email': 'attendee8@example.com',
  #                                                             'response': 0,
  #                                                             'add_taster': 'add_taster'})
  #   self.assertContains(response, "has been added to the party invitations list")

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='attendee8@example.com').exists())

  #   # invite new user
  #   response = self.client.post(reverse('party_details', args=[party.id]), {'party': party.id,
  #                                                             'first_name': 'New',
  #                                                             'last_name': 'Guy2',
  #                                                             'email': 'new.guy2@example.com',
  #                                                             'response': 0,
  #                                                             'add_taster': 'add_taster'})
  #   self.assertContains(response, "has been added to the party invitations list")

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='new.guy2@example.com').exists())

  # def old_test_rep_create_party(self):
  #   response = self.client.login(email='specialist2@example.com', password='hello')
  #   self.assertTrue(response)

  #   pro = User.objects.get(email='specialist2@example.com')

  #   response = self.client.get(reverse('main.views.party_add'))
  #   self.assertEquals(response.status_code, 200)

  #   # TODO: select host from list
  #   response = self.client.post(reverse('main.views.party_add'),  {'title': 'Weird Party',
  #                                                     'description': 'Just another weird party',
  #                                                     'phone': '555-617-6706',
  #                                                     'event_day': (timezone.now() + timedelta(days=10)).strftime('%m/%d/%Y'),
  #                                                     'event_time': '08:30',  # TODO: sort out this timezone warning
  #                                                     'first_name': 'New',
  #                                                     'last_name': 'Host',
  #                                                     'email': 'new.host@example.com',
  #                                                     'street1': '5 Kendall',
  #                                                     'city': 'Cambridge',
  #                                                     'state': 'MA',
  #                                                     'zipcode': '02139',
  #                                                     })
  #   self.assertRedirects(response, reverse('main.views.party_list'))

  #   party = Party.objects.get(title='Weird Party')

  #   self.assertTrue(MyHost.objects.filter(pro=pro, host__email='new.host@example.com').exists())

  #   self.assertTrue(OrganizedParty.objects.filter(party=party, pro=pro).exists())

  #   # check emails were sent
  #   new_host_email = Email.objects.filter(subject="Your Vinely Party has been Scheduled!", recipients="[u'new.host@example.com']")
  #   self.assertTrue(new_host_email.exists())

  #   welcome_email = Email.objects.filter(subject="Welcome to Vinely!", recipients="[u'new.host@example.com']")
  #   self.assertTrue(welcome_email.exists())

  #   # invite existing tasters
  #   response = self.client.get(reverse('main.views.party_taster_invite'))
  #   self.assertEquals(response.status_code, 200)

  #   # select taster from list
  #   invitee = User.objects.get(email='attendee2@example.com')

  #   response = self.client.post(reverse('main.views.party_taster_invite'),  {'party': party.id,
  #                                                           'invitee': invitee.id})

  #   self.assertRedirects(response, reverse('party_details', args=[party.id]))

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='attendee2@example.com').exists())

  #   # enter existing user in form
  #   response = self.client.post(reverse('main.views.party_taster_invite'),  {'party': party.id,
  #                                                           'first_name': 'Attendee',
  #                                                           'last_name': 'Four',
  #                                                           'email': 'attendee4@example.com'})
  #   self.assertRedirects(response, reverse('main.views.party_details', args=[party.id]))

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='attendee4@example.com').exists())

  #   # invite new user
  #   response = self.client.post(reverse('main.views.party_taster_invite'),  {'party': party.id,
  #                                                           'first_name': 'New',
  #                                                           'last_name': 'Guy',
  #                                                           'email': 'new.guy@example.com'})
  #   self.assertRedirects(response, reverse('main.views.party_details', args=[party.id]))

  #   self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='new.guy@example.com').exists())

    # TODO: Hit send invite and check if mails are sent

  def test_pro_create_party_for_host(self):
    response = self.client.login(email='specialist2@example.com', password='hello')
    self.assertTrue(response)

    pro = User.objects.get(email='specialist2@example.com')

    response = self.client.get(reverse('main.views.party_add'))
    self.assertEquals(response.status_code, 200)

    # 1. new host
    response = self.client.post(reverse('main.views.party_add'),  {'title': 'Another Weird Party',
                                                      'phone': '555-617-6706',
                                                      'event_day': (timezone.now() + timedelta(days=10)).strftime('%m/%d/%Y'),
                                                      'event_time': '08:30 PM',
                                                      'first_name': 'New',
                                                      'last_name': 'Host',
                                                      'email': 'new.host@example.com',
                                                      'street1': '5 Kendall',
                                                      'city': 'Cambridge',
                                                      'state': 'MA',
                                                      'zipcode': '02139',
                                                      'create': 'create'})

    party = Party.objects.get(title='Another Weird Party', host__email='new.host@example.com')
    self.assertRedirects(response, reverse('party_details', args=[party.id]))

    self.assertTrue(party.host.userprofile.is_host())
    self.assertEquals(party.host.userprofile.current_pro, pro)

    self.assertTrue(OrganizedParty.objects.filter(party=party, pro=pro).exists())

    # check emails were sent
    # to host
    new_host_email = Email.objects.filter(subject="Your Vinely Taste Party has been scheduled!", sender='Party Confirmation <sales@vinely.com>', recipients="[u'new.host@example.com']")
    self.assertTrue(new_host_email.exists())

    #to pro and care
    pro_care_email = Email.objects.filter(subject="Your Vinely Party has been scheduled!", recipients="[u'specialist2@example.com', u'care@vinely.com']")
    self.assertTrue(pro_care_email.exists())

    welcome_email = Email.objects.filter(subject="Welcome to Vinely!", recipients="[u'new.host@example.com']")
    self.assertTrue(welcome_email.exists())

    # 2. existing host
    response = self.client.post(reverse('main.views.party_add'),  {'title': 'Host Party',
                                                      'phone': '555-617-6706',
                                                      'event_day': (timezone.now() + timedelta(days=10)).strftime('%m/%d/%Y'),
                                                      'event_time': '08:30 PM',
                                                      'first_name': 'New',
                                                      'last_name': 'Host',
                                                      'email': 'host1@example.com',
                                                      'street1': '5 Kendall',
                                                      'city': 'Cambridge',
                                                      'state': 'MA',
                                                      'zipcode': '02139',
                                                      'create': 'create'})

    party = Party.objects.get(title='Host Party', host__email='host1@example.com')
    self.assertRedirects(response, reverse('party_details', args=[party.id]))

    self.assertEquals(party.host.userprofile.current_pro, pro)

    self.assertTrue(OrganizedParty.objects.filter(party=party, pro=pro).exists())

    # check emails were sent
    # to host
    new_host_email = Email.objects.filter(subject="Your Vinely Taste Party has been scheduled!", sender='Party Confirmation <sales@vinely.com>', recipients="[u'new.host@example.com']")
    self.assertTrue(new_host_email.exists())

    #to pro and care
    pro_care_email = Email.objects.filter(subject="Your Vinely Party has been scheduled!", recipients="[u'specialist2@example.com', u'care@vinely.com']")
    self.assertTrue(pro_care_email.exists())

    welcome_email = Email.objects.filter(subject="Welcome to Vinely!", recipients="[u'host1@example.com']")
    self.assertFalse(welcome_email.exists())

  def host_complete_party_setup(self):
    from main.utils import get_default_invite_message, get_default_signature

    response = self.client.login(email='host1@example.com', password='hello')
    self.assertTrue(response)

    host = User.objects.get(email='host1@example.com')

    party = self.create_party()
    party.confirmed = False
    party.save()

    response = self.client.post(reverse('party_add', args=[party.id]), {
        'first_name': 'host.first_name',
        'last_name': 'host.last_name',
        'email': host.email,
        'title': party.title,
        'event_time': party.event_date.strftime('%H:%M'),
        'event_day': party.event_date.strftime('%m/%d/%Y'),
        'party_id': party.id,
        'street1': party.address.street1,
        'zipcode': party.address.zipcode,
        'phone': '555-617-6706',
        'state': party.address.state,
        'city': party.address.city,
        'next': 'next',
    })

    self.assertRedirects(response, reverse('party_write_invitation', args=[party.id]))

    response = self.client.post(reverse('party_write_invitation', args=[party.id]), {
        'custom_message': get_default_invite_message(party),
        'signature': get_default_signature(party),
        'custom_subject': "You've been invited to a Vinely Party",
        'party': party.id,
        'next': 'next',
    })
    self.assertRedirects(response, reverse('party_find_friends', args=[party.id]))

    # Add invitee - new user
    response = self.client.post(reverse('party_find_friends', args=[party.id]), {
        'first_name': 'New',
        'last_name': 'Taster',
        'email': 'new.taster@example.com',
        'response': 0,
        'party': party.id,
        'add_taster': 'add_taster',
    })

    # ensure user is created
    invitee = User.objects.get(email='new.taster@example.com')
    self.assertFalse(invitee.is_active)

    self.assertContains(response, '%s %s (%s) has been added to the party invitations list.' % (invitee.first_name, invitee.last_name, invitee.email))

    # Taster added to invitees list
    invite = PartyInvite.objects.filter(invitee=invitee, party=party)
    self.assertTrue(invite.exists())

    # Add invitee - exiting user
    response = self.client.post(reverse('party_find_friends', args=[party.id]), {
        'first_name': 'Attendee',
        'last_name': 'Six',
        'email': 'attendee6@example.com',
        'response': 0,
        'party': party.id,
        'add_taster': 'add_taster',
    })
    invitee = User.objects.get(email='attendee6@example.com')
    self.assertTrue(invitee.is_active)
    # print response
    self.assertContains(response, '%s %s (%s) has been added to the party invitations list.' % (invitee.first_name, invitee.last_name, invitee.email))

    # Taster added to invitees list
    invite = PartyInvite.objects.filter(invitee=invitee, party=party)
    self.assertTrue(invite.exists())

    # 5. remove user invitation list
    # Add invitee - exiting user
    response = self.client.post(reverse('party_find_friends', args=[party.id]), {
        'first_name': 'Attendee',
        'last_name': 'Two',
        'email': 'host2@example.com',
        'response': 0,
        'party': party.id,
        'add_taster': 'add_taster',
    })
    invite = PartyInvite.objects.filter(invitee__email='host2@example.com', party=party)
    self.assertTrue(invite.exists())
    response = self.client.get("%s?next=%s" % (reverse('party_remove_taster', args=[invite[0].id]), reverse('party_find_friends', args=[party.id])))
    # redirects to party_friends
    self.assertEquals(response.status_code, 302)
    invite = PartyInvite.objects.filter(invitee__email='host2@example.com', party=party)
    self.assertFalse(invite.exists())

    response = self.client.post(reverse('party_find_friends', args=[party.id]), {
        'next': 'next',
    })

    self.assertRedirects(response, reverse('party_review_request', args=[party.id]))

    response = self.client.post(reverse('party_review_request', args=[party.id]), {
        'request_party': 'request_party',
        'auto_thank_you': 0,
        'taster_actions': [0],
        # 'taster_actions': [0, 1],
    })
    self.assertRedirects(response, reverse('party_details', args=[party.id]))

    party = Party.objects.get(id=party.id)
    self.assertTrue(party.auto_thank_you)
    self.assertTrue(party.guests_see_guestlist)
    self.assertFalse(party.guests_can_invite)

    # check emails were sent to pro
    party_confirmed_mail = Email.objects.filter(subject='host.first_name has completed setting up their party!', recipients="[u'specialist1@example.com', 'care@vinely.com']")
    self.assertTrue(party_confirmed_mail.exists())

    # check emails were sent to host
    host_email = Email.objects.filter(subject="You've been invited to a Vinely Party", recipients__in=["[u'new.taster@example.com']", "[u'attendee6@example.com']"])
    self.assertEquals(host_email.count(), 2)

  # def test_host_create_party_new_flow(self):

  #   response = self.client.login(email='host2@example.com', password='hello')
  #   self.assertTrue(response)

  #   response = self.client.get(reverse('party_add'))
  #   # cannot create party without a pro
  #   self.assertRedirects(response, reverse('party_list'))

  #   # 1. create party and hit save
  #   host = User.objects.get(email='host2@example.com')
  #   pro = User.objects.get(email='specialist1@example.com')
  #   MyHost.objects.create(pro=pro, host=host)
  #   response = self.client.post(reverse('main.views.party_add'),  {'title': 'Host2 Weird Party',
  #                                                     'description': 'Just another weird party',
  #                                                     'phone': '555-617-6706',
  #                                                     'event_day': (timezone.now() + timedelta(days=10)).strftime('%m/%d/%Y'),
  #                                                     'event_time': '08:30 PM',
  #                                                     'first_name': 'New',
  #                                                     'last_name': 'Host',
  #                                                     'email': 'new.host@example.com',
  #                                                     'street1': '5 Kendall',
  #                                                     'city': 'Grand Rapids',
  #                                                     'state': 'MI',
  #                                                     'zipcode': '49546',
  #                                                     'save': 'save',
  #                                                     })
  #   party = Party.objects.get(title='Host2 Weird Party', host=host)
  #   self.assertRedirects(response, reverse('party_add', args=[party.id]))

  #   self.assertTrue(MyHost.objects.filter(pro=pro, host=host).exists())
  #   self.assertTrue(OrganizedParty.objects.filter(party=party, pro=pro).exists())

  #   # 2. create party and hit next
  #   response = self.client.post(reverse('main.views.party_add'),  {'title': 'Host2 Second Party',
  #                                                     'phone': '555-617-6706',
  #                                                     'event_day': (timezone.now() + timedelta(days=10)).strftime('%m/%d/%Y'),
  #                                                     'event_time': '08:30 PM',
  #                                                     'first_name': 'New',
  #                                                     'last_name': 'Host',
  #                                                     'email': 'new.host@example.com',
  #                                                     'street1': '5 Kendall',
  #                                                     'city': 'Grand Rapids',
  #                                                     'state': 'MI',
  #                                                     'zipcode': '49546',
  #                                                     'next': 'next',
  #                                                     })
  #   party = Party.objects.get(title='Host2 Second Party', host=host)
  #   self.assertRedirects(response, reverse('party_write_invitation', args=[party.id]))

  #   self.assertTrue(MyHost.objects.filter(pro=pro, host=host).exists())
  #   self.assertTrue(OrganizedParty.objects.filter(party=party, pro=pro).exists())

  #   # write invitation - save
  #   response = self.client.get(reverse('party_write_invitation', args=[party.id]))
  #   self.assertEquals(response.status_code, 200)

  #   response = self.client.post(reverse('party_write_invitation', args=[party.id]), {'party': party.id,
  #                                                                                   'custom_subject': 'You are cordially invited',
  #                                                                                   'custom_message': 'Come ready to drink!',
  #                                                                                   'auto_invite': 1,
  #                                                                                   'auto_thank_you': 1,
  #                                                                                   'save': 'save',
  #                                                                                   })
  #   self.assertContains(response, "Your invitation message was successfully saved.")

  #   invitation_sent = InvitationSent.objects.get(party=party.id)
  #   party = invitation_sent.party

  #   self.assertFalse(party.auto_invite)
  #   self.assertFalse(party.auto_thank_you)
  #   self.assertFalse(party.guests_can_invite)

  #   # write invitation - next
  #   response = self.client.post(reverse('party_write_invitation', args=[party.id]), {'party': party.id,
  #                                                                                   'custom_subject': 'You are cordially invited',
  #                                                                                   'custom_message': 'Come ready to drink!',
  #                                                                                   'auto_invite': 0,
  #                                                                                   'auto_thank_you': 0,
  #                                                                                   'guests_can_invite': 1,
  #                                                                                   'next': 'next',
  #                                                                                   })
  #   self.assertRedirects(response, reverse('party_find_friends', args=[party.id]))

  #   party = Party.objects.get(id=party.id)
  #   self.assertTrue(party.auto_invite)
  #   self.assertTrue(party.auto_thank_you)
  #   self.assertTrue(party.guests_can_invite)

  #   # 3. invite new users
  #   response = self.client.post(reverse('party_details', args=[party.id]), {'party': party.id,
  #                                                                           'first_name': 'New',
  #                                                                           'last_name': 'Guy2',
  #                                                                           'email': 'new.guy2@example.com',
  #                                                                           'response': 0,
  #                                                                           'add_taster': 'add_taster'})
  #   self.assertContains(response, "has been added to the party invitations list")

  #   # 4. change options - save
  #   response = self.client.post(reverse('party_find_friends', args=[party.id]), {'save': 'save',
  #                                                                               })
  #   self.assertContains(response, 'The Party taster options were successfully saved.')

  #   party = Party.objects.get(id=party.id)
  #   self.assertTrue(party.auto_invite)
  #   self.assertTrue(party.auto_thank_you)
  #   self.assertFalse(party.guests_can_invite)
  #   self.assertFalse(party.guests_see_guestlist)

  #   # 5. remove user invitation list
  #   invite = PartyInvite.objects.get(party=party, invitee__email='new.guy2@example.com')
  #   response = self.client.get("%s?next=%s" % (reverse('party_remove_taster', args=[invite.id]), reverse('party_find_friends', args=[party.id])))
  #   # redirects to party_friends
  #   self.assertEquals(response.status_code, 302)
  #   # self.assertRedirects(response, reverse('party_find_friends', args=[party.id]))

  #   # 6. change options - request pro
  #   response = self.client.post(reverse('party_find_friends', args=[party.id]), {'request': 'request', 'taster_actions': [0, 1]})
  #   self.assertRedirects(response, reverse('party_details', args=[party.id]))

  #   party = Party.objects.get(id=party.id)
  #   self.assertTrue(party.auto_invite)
  #   self.assertTrue(party.auto_thank_you)
  #   self.assertTrue(party.guests_can_invite)
  #   self.assertTrue(party.guests_see_guestlist)
  #   self.assertTrue(party.requested)

  #   # check emails were sent to pro
  #   party_request_mail = Email.objects.filter(subject__icontains="would like to host a party", recipients="[u'specialist1@example.com']")
  #   self.assertTrue(party_request_mail.exists())

  #   # check emails were sent to host
  #   host_email = Email.objects.filter(subject="Your Vinely Party has been Scheduled!", recipients="[u'host2@example.com']")
  #   self.assertTrue(host_email.exists())

  def test_rep_adding_ratings(self):

    party = self.create_party()

    # try adding ratings if you are not pro of that party
    response = self.client.login(email='specialist2@example.com', password='hello')
    self.assertTrue(response)

    response = self.client.get(reverse('personality.views.record_all_wine_ratings', args=['attendee1@example.com', party.id]))
    self.assertRedirects(response, reverse('main.views.party_list'))

    self.client.logout()

    # login with rep
    response = self.client.login(email='specialist1@example.com', password='hello')
    self.assertTrue(response)

    # NOTE: View not being used
    # response = self.client.get(reverse('personality.views.record_wine_ratings'))
    # self.assertEquals(response.status_code, 200)

    response = self.client.get(reverse('personality.views.record_all_wine_ratings', args=['attendee1@example.com', party.id]))
    self.assertEquals(response.status_code, 200)

    # attendee must have been in the party invite
    response = self.client.get(reverse('personality.views.record_all_wine_ratings', args=['attendee6@example.com', party.id]))
    self.assertRedirects(response, reverse('main.views.party_list'))

    # TODO: add new user from add taster form
    response = self.client.post(reverse('personality.views.record_all_wine_ratings',
                                        args=["attendee1@example.com", party.id]), {'email': 'new.taster@example.com',
                                                                                    'first_name': 'New',
                                                                                    'last_name': 'Taster',
                                                                                    'add_taster': 'add_taster'})
    self.assertRedirects(response, reverse('personality.views.record_all_wine_ratings', args=['new.taster@example.com', party.id]))

    # ensure linked to party
    self.assertTrue(PartyInvite.objects.filter(party=party, invitee__email='new.taster@example.com').exists())

    # ensure emails sent
    welcome_email = Email.objects.filter(subject="Welcome to Vinely!", recipients="[u'new.taster@example.com']")
    self.assertTrue(welcome_email.exists())

    # add an attendee information
    # type in the rating information
    response = self.client.post(reverse('personality.views.record_all_wine_ratings',
                                        args=["attendee1@example.com", party.id]), {'email': 'attendee1@example.com',
                                                        'save_ratings': "save_ratings",
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

    pro = User.objects.get(email="specialist1@example.com")
    host = User.objects.get(email="host1@example.com")
    address = Address.objects.create(street1="65 Gordon St.",
                                      city="Grand Rapids",
                                      state="MI",
                                      zipcode="49546-2342")

    party = Party.objects.create(host=host, title="John's party", description="Wine party on a sizzling hot day",
                              address=address, event_date=timezone.now() + timedelta(days=10))

    OrganizedParty.objects.create(pro=pro, party=party)
    # invite people
    attendees = ['attendee1@example.com',
                  'attendee2@example.com',
                  'attendee3@example.com',
                  'attendee4@example.com',
                  'attendee5@example.com']
    import uuid
    for att in attendees:
      PartyInvite.objects.create(party=party, invitee=User.objects.get(email=att), rsvp_code=str(uuid.uuid4()))

    return party

  def vinely_card_processing(self):
    ##########################################################
    #
    # Using Vinely Credit card processing
    #
    ##########################################################
    year = datetime.today().year + 5
    response = self.client.post(reverse("main.views.edit_credit_card"), {"card_number": "4111111111111",
                                                                        "exp_month": 6,
                                                                        "exp_year": year,
                                                                        "verification_code": 111,
                                                                        "billing_zipcode": "02139",
                                                                        "card_type": "Unknown"})
    return response

  def stripe_card_processing(self, user):
    ##########################################################
    #
    # Using Stripe Credit card processing
    #
    ##########################################################

    import stripe
    from django.conf import settings

    stripe.api_key = settings.STRIPE_SECRET_CA
    year = datetime.today().year + 5
    token = stripe.Token.create(card={'number': 4242424242424242, "name": "%s %s" % (user.first_name, user.last_name), 'exp_month': 12, 'exp_year': year, 'cvc': 123, 'address_zip': '02139'})

    response = self.client.post(reverse("main.views.edit_credit_card"), {"stripe_token": token.id,
                                                                        "exp_month": token.card.exp_month,
                                                                        "exp_year": token.card.exp_year,
                                                                        "last4": token.card.last4,
                                                                        "address_zip": token.card.address_zip,
                                                                        "card_type": token.card.type})
    return response

  def test_rep_adding_orders(self):
    party = self.create_party()

    real_attendee = User.objects.get(email='attendee1@example.com')

    response = self.client.login(email="specialist2@example.com", password="hello")
    self.assertTrue(response)

    # try with party that you are not the pro
    response = self.client.get(reverse('main.views.start_order', args=[real_attendee.id, party.id]))
    self.assertRedirects(response, reverse('main.views.party_list'))

    self.client.logout()

    response = self.client.login(email="specialist1@example.com", password="hello")
    self.assertTrue(response)

    # try with wrong attendee
    fake_attendee = User.objects.get(email='attendee6@example.com')
    response = self.client.get(reverse('main.views.start_order', args=[fake_attendee.id, party.id]))
    self.assertRedirects(response, reverse('main.views.party_list'))

    # now with real taster and real party
    response = self.client.get(reverse('main.views.start_order', args=[real_attendee.id, party.id]))
    self.assertRedirects(response, reverse("main.views.cart_add_wine"))

    case = Product.objects.get(name="3 Bottles")
    response = self.client.post(reverse("main.views.cart_add_wine"), {"product": case.id,
                                                                      "quantity": 2,
                                                                      "frequency": 0,
                                                                      "total_price": 108.00})
    self.assertRedirects(response, reverse("main.views.cart"))

    birth_date = timezone.now() - timedelta(days=30 * 365)

    response = self.client.post(reverse("main.views.edit_shipping_address"), {"eligibility-dob": birth_date.strftime('%m/%d/%Y'),
                                                                              "first_name": "John",
                                                                              "last_name": "Doe",
                                                                              "address1": "65 Gordon St.",
                                                                              "city": "Cambridge",
                                                                              "state": "MA",
                                                                              "zipcode": "02139",
                                                                              "phone": "555-617-6706",
                                                                              "email": "attendee1@example.com"})
    self.assertContains(response, 'Currently, we can only ship to California.')

    response = self.client.post(reverse("main.views.edit_shipping_address"), {"eligibility-dob": birth_date.strftime('%m/%d/%Y'),
                                                                              "first_name": "John",
                                                                              "last_name": "Doe",
                                                                              "address1": "65 Gordon St.",
                                                                              "city": "San Fransisco",
                                                                              "state": "CA",
                                                                              "zipcode": "92612",
                                                                              "phone": "555-617-6706",
                                                                              "email": "attendee1@example.com"})
    response = self.stripe_card_processing(real_attendee)
    self.assertRedirects(response, reverse("main.views.place_order"))

    response = self.client.post(reverse("main.views.place_order"))
    order = Order.objects.get(cart__items__product=case)

    self.assertRedirects(response, reverse("main.views.order_complete", args=[order.order_id]))

    response = self.client.get(reverse("main.views.order_complete", args=[order.order_id]))
    self.assertEquals(response.status_code, 200)

    self.assertTrue(Order.objects.filter(cart__items__product=case).exists())

    # check emails sent
    recipient_email = Email.objects.filter(subject="Your Vinely order was placed successfully!", recipients="[u'attendee1@example.com']")
    self.assertTrue(recipient_email.exists())

    subject = "Order ID: %s has been submitted for %s!" % (order.vinely_order_id, order.shipping_address.state)
    vinely_email = Email.objects.filter(subject=subject, recipients="['fulfillment@vinely.com']")
    self.assertTrue(vinely_email.exists())

  def test_attendee_ordering(self):
    response = self.client.login(email="attendee1@example.com", password="hello")
    self.assertTrue(response)

    response = self.client.get(reverse('main.views.start_order'))
    self.assertRedirects(response, reverse("main.views.cart_add_wine"))

    case = Product.objects.get(name="6 Bottles", unit_price=97.00)

    response = self.client.post(reverse("main.views.cart_add_wine"), {"product": case.id,
                                                                      "quantity": 2,
                                                                      "frequency": 0,
                                                                      "total_price": 194.00})
    self.assertRedirects(response, reverse("main.views.cart"))

    birth_date = timezone.now() - timedelta(days=30 * 365)

    response = self.client.post(reverse("main.views.edit_shipping_address"), {"first_name": "John",
                                                                              "last_name": "Doe",
                                                                              "address1": "65 Gordon St.",
                                                                              "city": "Cambridge",
                                                                              "state": "MA",
                                                                              "zipcode": "02139",
                                                                              "phone": "555-617-6706",
                                                                              "email": "attendee1@example.com"})

    self.assertContains(response, 'Currently, we can only ship to California.')

    response = self.client.post(reverse("main.views.edit_shipping_address"), {"first_name": "John",
                                                                              "last_name": "Doe",
                                                                              "address1": "65 Gordon St.",
                                                                              "city": "San FranciscoZ",
                                                                              "state": "CA",
                                                                              "zipcode": "92612",
                                                                              "phone": "555-617-6706",
                                                                              "email": "attendee1@example.com"})
    self.assertContains(response, "You cannot order wine until you verify that you are not under 21")

    response = self.client.post(reverse("main.views.edit_shipping_address"), {"eligibility-dob": birth_date.strftime('%m/%d/%Y'),
                                                                              "first_name": "John",
                                                                              "last_name": "Doe",
                                                                              "address1": "65 Gordon St.",
                                                                              "city": "San Fransisco",
                                                                              "state": "CA",
                                                                              "zipcode": "92612",
                                                                              "phone": "555-617-6706",
                                                                              "email": "attendee1@example.com"})
    self.assertRedirects(response, reverse("main.views.edit_credit_card"))
    taster = User.objects.get(email='attendee1@example.com')
    response = self.stripe_card_processing(taster)

    self.assertRedirects(response, reverse("main.views.place_order"))

    response = self.client.post(reverse("main.views.place_order"))
    order = Order.objects.get(cart__items__product=case)

    self.assertRedirects(response, reverse("main.views.order_complete", args=[order.order_id]))

    response = self.client.get(reverse("main.views.order_complete", args=[order.order_id]))
    self.assertEquals(response.status_code, 200)

    self.assertTrue(Order.objects.filter(cart__items__product=case).exists())

    # check emails sent
    recipient_email = Email.objects.filter(subject="Your Vinely order was placed successfully!", recipients="[u'attendee1@example.com']")
    self.assertTrue(recipient_email.exists())

    subject = "Order ID: %s has been submitted for %s!" % (order.vinely_order_id, order.shipping_address.state)
    vinely_email = Email.objects.filter(subject=subject, recipients="['fulfillment@vinely.com']")
    self.assertTrue(vinely_email.exists())

  def test_product_ordering(self):
    """
    test host order tasting kit
    """
    party = self.create_party()

    response = self.client.login(email="host1@example.com", password="hello")
    self.assertTrue(response)

    response = self.client.get(reverse("main.views.cart_add_tasting_kit", args=[party.id]))

    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("main.views.cart_add_tasting_kit", args=[party.id]), {"product": 100,
                                                                                              "quantity": 2,
                                                                                              "price_category": 0,
                                                                                              "frequency": 0,
                                                                                              "total_price": 100})
    self.assertContains(response, "Select a valid choice.")

    kit = Product.objects.get(name="Vinely's First Taste Kit", unit_price=99.00)

    response = self.client.post(reverse("main.views.cart_add_tasting_kit", args=[party.id]), {"product": kit.id,
                                                                                              "quantity": 2,
                                                                                              "price_category": 0,
                                                                                              "frequency": 0,
                                                                                              "total_price": 140.00})
    self.assertRedirects(response, reverse("main.views.cart"))

    party2 = self.create_party()

    response = self.client.get(reverse("main.views.cart_add_tasting_kit", args=[party2.id]))
    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("main.views.cart_add_tasting_kit", args=[party2.id]), {"product": kit.id,
                                                                                                "quantity": 2,
                                                                                                "price_category": 0,
                                                                                                "frequency": 0,
                                                                                                "total_price": 140.00})
    # redirects to same page with error message
    self.assertRedirects(response, reverse("main.views.cart_add_tasting_kit", args=[party2.id]))
    # self.assertContains(response, "You can only order taste kits for one party at a time.")

    case = Product.objects.get(name="6 Bottles", unit_price=97.00)
    response = self.client.post(reverse("main.views.cart_add_wine"), {"product": case.id,
                                                                      "quantity": 2,
                                                                      # "price_category": 0,
                                                                      "frequency": 0,
                                                                      "total_price": 194.00})
    # redirects to same page with error message
    self.assertRedirects(response, reverse("main.views.cart_add_wine"))
    # self.assertContains(response, 'A tasting kit is already in your cart')

    response = self.client.get(reverse("main.views.edit_shipping_address"))
    self.assertEquals(response.status_code, 200)

    response = self.client.post(reverse("main.views.edit_shipping_address"), {"first_name": "John",
                                                                              "last_name": "Doe",
                                                                              "address1": "65 Gordon St.",
                                                                              "city": "Cambridge",
                                                                              "state": "MA",
                                                                              "zipcode": "02139",
                                                                              "phone": "555-617-6706",
                                                                              "email": "host1@example.com"})
    self.assertContains(response, "You cannot order wine until you verify that you are not under 21")

    birth_date = timezone.now() - timedelta(days=30 * 365)

    # check switch between stripe and vinely credit cards
    # response = self.client.post(reverse("main.views.edit_shipping_address"), {"eligibility-dob": birth_date.strftime('%m/%d/%Y'),
    #                                                                           "first_name": "John",
    #                                                                           "last_name": "Doe",
    #                                                                           "address1": "65 Gordon St.",
    #                                                                           "city": "Grand Rapids",
    #                                                                           "state": "MI",
    #                                                                           "zipcode": "49546",
    #                                                                           "phone": "555-617-6706",
    #                                                                           "email": "host1@example.com"})
    # self.assertRedirects(response, reverse("main.views.edit_credit_card"))

    # response = self.client.get(reverse("main.views.edit_credit_card"))
    # self.assertContains(response, "Stripe.setPublishableKey")

    # check zipcode supported
    response = self.client.post(reverse("main.views.edit_shipping_address"), {"eligibility-dob": birth_date.strftime('%m/%d/%Y'),
                                                                              "first_name": "John",
                                                                              "last_name": "Doe",
                                                                              "address1": "65 Gordon St.",
                                                                              "city": "Cambridge",
                                                                              "state": "MA",
                                                                              "zipcode": "02139",
                                                                              "phone": "555-617-6706",
                                                                              "email": "host1@example.com"})
    # self.assertContains(response, "Vinely does not currently operate in the specified area")
    self.assertContains(response, 'Currently, we can only ship to California.')
    # self.assertContains(response, "You cannot order wine until you verify that you are not under 21")
    birth_date = timezone.now() - timedelta(days=30 * 365)

    response = self.client.post(reverse("main.views.edit_shipping_address"), {"eligibility-dob": birth_date.strftime('%m/%d/%Y'),
                                                                              "first_name": "John",
                                                                              "last_name": "Doe",
                                                                              "address1": "65 Gordon St.",
                                                                              "city": "Cambridge",
                                                                              "state": "CA",
                                                                              "zipcode": "92612",
                                                                              "phone": "555-617-6706",
                                                                              "email": "host1@example.com"})
    self.assertRedirects(response, reverse("main.views.edit_credit_card"))

    taster = User.objects.get(email='host1@example.com')
    response = self.stripe_card_processing(taster)

    self.assertRedirects(response, reverse("main.views.place_order"))

    response = self.client.post(reverse("main.views.place_order"))
    order = Order.objects.get(cart__items__product=kit)

    self.assertRedirects(response, reverse("main.views.order_complete", args=[order.order_id]))

    # check emails sent
    recipient_email = Email.objects.filter(subject="Your Vinely order was placed successfully!", recipients="[u'host1@example.com']")
    self.assertTrue(recipient_email.exists())

    subject = "Order ID: %s has been submitted for %s!" % (order.vinely_order_id, order.shipping_address.state)
    vinely_email = Email.objects.filter(subject=subject, recipients="['fulfillment@vinely.com']")
    self.assertTrue(vinely_email.exists())

    self.client.logout()
