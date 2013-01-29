"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from main.models import Product, Order, Cart, LineItem, CustomizeOrder
from accounts.models import Address, CreditCard
from support.models import Wine, WineInventory
from personality.models import WineRatingData
from main.utils import UTC

from django.contrib.auth.models import User
from django.test.client import Client

from datetime import datetime


class SimpleTest(TestCase):

    fixtures = ['test_data.yaml']

    def runTest(self):
      pass

    def setUp(self):
      self.client = Client()

      # add wine inventory
      wine = Wine(name="2011 Loca Macabeo", year=2011, sku="VW200101-1", vinely_category=1, vinely_category2=1)
      wine.save()
      inv = WineInventory(wine=wine, on_hand=12)
      inv.save()

      wine = Wine(name="2009 Pinot Noir", year=2009, sku="VW200901-1", vinely_category=2, vinely_category2=2)
      wine.save()
      inv = WineInventory(wine=wine, on_hand=4)
      inv.save()

      u = User(email='attendee1@example.com')
      u.set_password('hello')
      u.save()

      u = User(email='attendee2@example.com')
      u.set_password('hello')
      u.save()

      u = User(email='attendee3@example.com')
      u.set_password('hello')
      u.save()

      u = User(email='jayme@vinely.com')
      u.set_password('hello')
      u.is_staff = True
      u.save()

      u = User(email='bethany@vinely.com')
      u.set_password('hello')
      u.is_staff = True
      u.save()

    def test_create_orders(self):
      # generate orders
      product = Product.objects.get(id=4)   # superior wine

      today = datetime.now(tz=UTC())

      user1 = User.objects.get(email='attendee1@example.com')
      prof1 = user1.get_profile()

      user2 = User.objects.get(email='attendee2@example.com')
      prof2 = user2.get_profile()

      user3 = User.objects.get(email='attendee3@example.com')
      prof3 = user3.get_profile()

      from personality.models import Wine
      tasting_wine1 = Wine.objects.get(id=1)
      tasting_wine2 = Wine.objects.get(id=2)
      tasting_wine3 = Wine.objects.get(id=3)
      tasting_wine4 = Wine.objects.get(id=4)
      tasting_wine5 = Wine.objects.get(id=5)
      tasting_wine6 = Wine.objects.get(id=6)

      # create wine rating data
      user1_rating1 = WineRatingData(user=user1, wine=tasting_wine1, overall=4)
      user1_rating1.save()
      user1_rating2 = WineRatingData(user=user1, wine=tasting_wine2, overall=3)
      user1_rating2.save()
      user1_rating3 = WineRatingData(user=user1, wine=tasting_wine3, overall=4)
      user1_rating3.save()
      user1_rating4 = WineRatingData(user=user1, wine=tasting_wine4, overall=2)
      user1_rating4.save()
      user1_rating5 = WineRatingData(user=user1, wine=tasting_wine5, overall=4)
      user1_rating5.save()
      user1_rating6 = WineRatingData(user=user1, wine=tasting_wine6, overall=1)
      user1_rating6.save()

      user2_rating1 = WineRatingData(user=user2, wine=tasting_wine1, overall=3)
      user2_rating1.save()
      user2_rating2 = WineRatingData(user=user2, wine=tasting_wine2, overall=4)
      user2_rating2.save()
      user2_rating3 = WineRatingData(user=user2, wine=tasting_wine3, overall=3)
      user2_rating3.save()
      user2_rating4 = WineRatingData(user=user2, wine=tasting_wine4, overall=4)
      user2_rating4.save()
      user2_rating5 = WineRatingData(user=user2, wine=tasting_wine5, overall=1)
      user2_rating5.save()
      user2_rating6 = WineRatingData(user=user2, wine=tasting_wine6, overall=4)
      user2_rating6.save()

      user3_rating1 = WineRatingData(user=user3, wine=tasting_wine1, overall=3)
      user3_rating1.save()
      user3_rating2 = WineRatingData(user=user3, wine=tasting_wine2, overall=3)
      user3_rating2.save()
      user3_rating3 = WineRatingData(user=user3, wine=tasting_wine3, overall=3)
      user3_rating3.save()
      user3_rating4 = WineRatingData(user=user3, wine=tasting_wine4, overall=3)
      user3_rating4.save()
      user3_rating5 = WineRatingData(user=user3, wine=tasting_wine5, overall=3)
      user3_rating5.save()
      user3_rating6 = WineRatingData(user=user3, wine=tasting_wine6, overall=3)
      user3_rating6.save()

      custom1 = CustomizeOrder(user=user1, wine_mix=0, sparkling=0)
      custom1.save()
      custom2 = CustomizeOrder(user=user2, wine_mix=1, sparkling=0)
      custom2.save()
      custom3 = CustomizeOrder(user=user3, wine_mix=2, sparkling=1)
      custom3.save()

      shipping_address1 = Address(street1="369 Franklin St. 101", city="Cambridge", state="MA", zipcode="02139")
      shipping_address1.save()
      shipping_address2 = Address(street1="369 Franklin St. 102", city="Cambridge", state="MA", zipcode="02139")
      shipping_address2.save()
      shipping_address3 = Address(street1="369 Franklin St. 103", city="Cambridge", state="MA", zipcode="02139")
      shipping_address3.save()

      prof1.shipping_address = shipping_address1
      prof1.save()
      prof2.shipping_address = shipping_address2
      prof2.save()
      prof3.shipping_address = shipping_address3
      prof3.save()

      card1 = CreditCard(card_number="4444111144441111", exp_month=12, exp_year=15)
      card1.save()

      card2 = CreditCard(card_number="4444111144441111", exp_month=12, exp_year=15)
      card2.save()

      card3 = CreditCard(card_number="4444111144441111", exp_month=12, exp_year=15)
      card3.save()

      item1 = LineItem(product=product, price_category=12, quantity=1, frequency=1, total_price=36.00)
      item1.save()

      item2 = LineItem(product=product, price_category=13, quantity=1, frequency=1, total_price=72.00)
      item2.save()

      item3 = LineItem(product=product, price_category=14, quantity=1, frequency=1, total_price=144.00)
      item3.save()

      cart1 = Cart(user=user1, receiver=user1, adds=1)
      cart1.save()
      cart1.items.add(item1)

      cart2 = Cart(user=user2, receiver=user2, adds=1)
      cart2.save()
      cart2.items.add(item2)

      cart3 = Cart(user=user3, receiver=user3, adds=1)
      cart3.save()
      cart3.items.add(item3)

      order1 = Order(ordered_by=user1, receiver=user1, cart=cart1, shipping_address=shipping_address1,
                    credit_card=card1, order_date=today)
      order1.assign_new_order_id()
      order1.save()

      order2 = Order(ordered_by=user2, receiver=user2, cart=cart2, shipping_address=shipping_address2,
                    credit_card=card2, order_date=today)
      order2.assign_new_order_id()
      order2.save()

      order3 = Order(ordered_by=user3, receiver=user3, cart=cart3, shipping_address=shipping_address3,
                    credit_card=card3, order_date=today)
      order3.assign_new_order_id()
      order3.save()

    def test_file_upload(self):

      self.client.login(email="jayme@vinely.com", password="hello")

      # upload a sample wine inventory data
      with open("data/wine_db_125.xlsx") as fp:
        response = self.client.post(reverse("support:wine_inventory"), {"inventory_file": fp,
                                                                                "comment": "This is good inventory"})

      # check that the models have been updated
      self.assertEqual(WineInventory.objects.all().count(), 34)

      sum_on_hand = 0
      for w in WineInventory.objects.all():
        sum_on_hand += w.on_hand

      self.assertEqual(sum_on_hand, 298)

      with open("data/wine_inventory_bad.xlsx") as fp:
        response = self.client.post(reverse("support:wine_inventory"), {"inventory_file": fp,
                                                                                "comment": "This is a bad inventory"})

      self.assertContains(response, "Not a valid inventory")
      # test some corner and abnormal cases
      self.assertEqual(WineInventory.objects.all().count(), 34)

      total_wines = 0
      for w in WineInventory.objects.all():
        total_wines += w.on_hand
      self.assertEqual(total_wines, 298)

    def test_wine_order_processing(self):
      # generate orders
      self.test_create_orders()

      self.client.login(email='jayme@vinely.com', password='hello')
      # look at the inventory and fulfill
      response = self.client.get(reverse("support:view_orders"))

      # check those orders that have warning
      self.assertContains(response, "Orders")

      order = Order.objects.filter(fulfill_status=Order.FULFILL_CHOICES[5][0])[0]
      self.assertContains(response, order.vinely_order_id)
      self.assertContains(response, "Needs Manual Review")

      # check wine quantities have been updated
      inv = WineInventory.objects.filter(wine__name="2011 Loca Macabeo")[0]
      self.assertEqual(inv.on_hand, 9)

    def test_manual_edit_order(self):

      self.client.login(email='jayme@vinely.com', password='hello')

      self.test_create_orders()

      response = self.client.get(reverse("support:view_orders"))

      order = Order.objects.filter(fulfill_status=Order.FULFILL_CHOICES[5][0])[0]

      # show order list
      response = self.client.get(reverse("support:edit_order", args=(order.id, )))

      self.assertContains(response, "Edit Order")

      # show view to edit and order
      wine1 = Wine.objects.get(sku="VW200101-1")
      wine2 = Wine.objects.get(sku="VW200901-1")

      inv1 = WineInventory.objects.get(wine=wine1)
      inv2 = WineInventory.objects.get(wine=wine2)

      # manually change/add wine slots
      response = self.client.post(reverse("support:edit_order", args=(order.id, )), {
                                                                        "form-TOTAL_FORMS": 6,
                                                                        "form-INITIAL_FORMS": 6,
                                                                        "form-MAX_NUM_FORMS": 6,
                                                                        "form-0-wine": wine1.id,
                                                                        "form-1-wine": wine2.id,
                                                                        "form-2-wine": wine1.id,
                                                                        "form-3-wine": wine1.id,
                                                                        "form-4-wine": wine2.id,
                                                                        "form-5-wine": wine2.id
                                                                      })

      self.assertContains(response, "Saved order details")
      #self.assertContains(response, "Saved order details.")

    def test_complete_order(self):

      self.client.login(email='jayme@vinely.com', password='hello')
      # complete some of the orders
      response = self.client.post(reverse("support:download_ready_orders"), {
                                                                      "orders": [1, 2]
                                                                    })
      # output excel file
      self.assertEquals(response.get('Content-Disposition'), 'attachment; filename=vinely_ready_orders.csv')

    def test_rate_the_wine(self):

      w_total = 0
      for w in WineInventory.objects.all():
        w_total += w.on_hand
      print "Total Wine bottles", w_total
      self.assertNotEqual(w_total, 0)

      # generate orders
      self.test_create_orders()

      self.client.login(email='jayme@vinely.com', password='hello')
      # look at the inventory and fulfill
      response = self.client.get(reverse("support:view_orders"))

      self.client.login(email='bethany@vinely.com', password='hello')

      # check the edit order view to see if past ratings are showing up
      response = self.client.get(reverse("support:view_past_orders"))

      order = Order.objects.filter(fulfill_status=Order.FULFILL_CHOICES[6][0])[0]
      self.assertContains(response, order.vinely_order_id)

      order = Order.objects.filter(fulfill_status=Order.FULFILL_CHOICES[6][0])[0]
      # open the wine rating page
      response = self.client.get(reverse("support:view_past_orders", args=(order.id,)))

      # should be able to see the wines that shipped
      self.assertContains(response, "2011 Loca Macabeo")

      # open the wine rating page
      response = self.client.get(reverse("support:view_past_orders", args=(3, )))

      self.assertEqual(response.status_code, 404)

      wine1 = Wine.objects.get(sku="VW200101-1")
      wine2 = Wine.objects.get(sku="VW200901-1")

      # rate the wine by going to the completed order (ratings 1 through 5)
      # save the wine order
      response = self.client.post(reverse("support:view_past_orders", args=(order.id, )), {
                                                                        "form-TOTAL_FORMS": 3,
                                                                        "form-INITIAL_FORMS": 3,
                                                                        "form-MAX_NUM_FORMS": 3,
                                                                        "form-0-overall_rating": 5,
                                                                        "form-1-overall_rating": 3,
                                                                        "form-2-overall_rating": 1,
                                                                        "form-0-order": order.id,
                                                                        "form-1-order": order.id,
                                                                        "form-2-order": order.id,
                                                                        "form-0-wine": wine1.id,
                                                                        "form-1-wine": wine2.id,
                                                                        "form-2-wine": wine1.id
                                                                      })

      self.assertContains(response, "Saved ratings for")

    def test_wine_order_processing_post_rating(self):

      self.client.login(email='jayme@vinely.com', password='hello')

      self.test_create_orders()

      # run the algorithm to check whether the new ratings reflect the fulfillment of certain orders
      response = self.client.get(reverse("support:view_orders"))

      # check wine quantities have been updated
      inv = WineInventory.objects.filter(wine__name="2011 Loca Macabeo")[0]
      self.assertEqual(inv.on_hand, 9)
