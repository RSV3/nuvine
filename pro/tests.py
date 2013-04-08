"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from datetime import datetime

from django.contrib.auth.models import User
from main.models import Question, Cart, LineItem, Order, Party, OrganizedParty, MyHost
from accounts.models import Address, UserProfile, CreditCard
from pro.utils import create_party, create_orders


class SimpleTest(TestCase):

    def setUp(self):
      for i in range(1, 14):
        pro = User(email="pro%d@gmail.com" % i, first_name="Pro%d" % i, last_name="Last%d" % i)
        pro.save()

      for i in range(1, 104):
        taster = User(email="taster%d@gmail.com" % i, first_name="Taster%d" % i, last_name="Last%d" % i)
        taster.save()

      for i in range(1, 14):
        host = User(email="host%d@gmail.com" % i, first_name="Host%d" % i, last_name="Last%d" % i)
        host.save()

    def runTest(self):
      pass

    def create_receiver_order_party(receiver, party, pro):
      """
        Method to easily create orders for a party and pro
      """
      pass

    def test_generate_users(self):
      """
        Create Pros, Tasters and Hosts
      """
      pass

    def test_generate_simulated_orders(self):
      """
        Create parties and create orders for those parties
      """

      # party 1
      party_id = 1
      pro = User.objects.get(email="pro1@gmail.com")
      host = User.objects.get(email="host1@gmail.com")
      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [1, 2, 3, 4, 5, 6, 28, 29]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=10, hour=19)
      party1 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party1_orders1 = [[1, 100, 0],
                        [2, 100, 1],
                        [3, 100, 0],
                        [4, 100, 1],
                        [5, 100, 0],
                        [6, 100, 1]]
      order_date1 = datetime(year=2013, month=3, day=10, hour=21)
      create_orders(party1, party1_orders1, order_date1)

      party1_orders2 = [[28, 100, 1],
                        [29, 100, 0]]
      order_date2 = datetime(year=2013, month=3, day=14, hour=21)
      create_orders(party1, party1_orders2, order_date2)

      # party 2
      party_id = 2
      pro = User.objects.get(email="pro2@gmail.com")
      host = User.objects.get(email="host2@gmail.com")
      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [7, 8, 9, 10, 30, 31]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=11, hour=19)
      party2 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party2_orders1 = [[7, 100, 0],
                        [8, 100, 1],
                        [9, 100, 0],
                        [10, 100, 1]]
      order_date1 = datetime(year=2013, month=3, day=11, hour=21)
      create_orders(party2, party2_orders1, order_date1)

      party2_orders2 = [[30, 100, 1],
                        [31, 100, 0]]
      order_date2 = datetime(year=2013, month=3, day=14, hour=21)
      create_orders(party2, party2_orders2, order_date2)

      # party 3
      party_id = 3
      pro = User.objects.get(email="pro3@gmail.com")
      host = User.objects.get(email="host3@gmail.com")
      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [11, 12, 13, 14, 15, 16, 17, 18, 19]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=12, hour=19)
      party3 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party3_orders1 = [[11, 100, 0],
                        [12, 100, 1],
                        [13, 100, 0],
                        [14, 100, 1],
                        [15, 100, 0],
                        [16, 100, 1],
                        [17, 100, 0],
                        [18, 100, 1],
                        [19, 100, 0]]
      order_date1 = datetime(year=2013, month=3, day=12, hour=21)
      create_orders(party3, party3_orders1, order_date1)

      # party 4
      party_id = 4
      pro = User.objects.get(email="pro4@gmail.com")
      host = User.objects.get(email="host4@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [20, 21, 22, 23, 24, 25, 26, 27]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=13, hour=19)
      party4 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party4_orders1 = [[20, 100, 1],
                        [21, 100, 0],
                        [22, 100, 1],
                        [23, 100, 0],
                        [24, 100, 1],
                        [25, 100, 0],
                        [26, 100, 1],
                        [27, 100, 0]]
      order_date1 = datetime(year=2013, month=3, day=13, hour=21)
      create_orders(party4, party4_orders1, order_date1)

      # party 5
      party_id = 5
      pro = User.objects.get(email="pro5@gmail.com")
      host = User.objects.get(email="host5@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [32, 33, 34, 35, 36]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=14, hour=19)
      party5 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party5_orders1 = [[32, 100, 1],
                        [33, 100, 0],
                        [34, 100, 1],
                        [35, 100, 0],
                        [36, 100, 1]]
      order_date1 = datetime(year=2013, month=3, day=14, hour=21)
      create_orders(party5, party5_orders1, order_date1)

      # TODO: Need to add a order that is not party related

      # party 6
      party_id = 6
      pro = User.objects.get(email="pro6@gmail.com")
      host = User.objects.get(email="host6@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [38, 39, 40, 41, 42, 43, 44, 45, 46, 47]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=15, hour=19)
      party6 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party6_orders1 = [[38, 100, 1],
                        [39, 100, 0],
                        [40, 100, 1],
                        [41, 100, 0],
                        [42, 100, 1],
                        [43, 100, 0],
                        [44, 100, 1],
                        [45, 100, 0],
                        [46, 100, 1],
                        [47, 100, 0]]
      order_date1 = datetime(year=2013, month=3, day=15, hour=21)
      create_orders(party6, party6_orders1, order_date1)

      # party 7
      party_id = 7
      pro = User.objects.get(email="pro7@gmail.com")
      host = User.objects.get(email="host7@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [48, 49, 50, 51, 52, 53, 54, 55, 56]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=16, hour=19)
      party7 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party7_orders1 = [[48, 100, 1],
                        [49, 100, 0],
                        [50, 100, 1],
                        [51, 100, 0],
                        [52, 100, 1],
                        [53, 100, 0],
                        [54, 100, 1],
                        [55, 100, 0],
                        [56, 100, 1]]
      order_date1 = datetime(year=2013, month=3, day=16, hour=21)
      create_orders(party7, party7_orders1, order_date1)

      # TODO: add order by Taster57 on 17th

      # party 8
      party_id = 8
      pro = User.objects.get(email="pro8@gmail.com")
      host = User.objects.get(email="host8@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [58, 59, 60, 61, 62, 63, 64, 65]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=18, hour=19)
      party8 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party8_orders1 = [[58, 100, 1],
                        [59, 100, 0],
                        [60, 100, 1],
                        [61, 100, 0],
                        [62, 100, 1],
                        [63, 100, 0],
                        [64, 100, 1],
                        [65, 100, 0]]
      order_date1 = datetime(year=2013, month=3, day=18, hour=21)
      create_orders(party8, party8_orders1, order_date1)

      # party 9
      party_id = 9
      pro = User.objects.get(email="pro9@gmail.com")
      host = User.objects.get(email="host9@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [66, 67, 68, 69, 70, 71]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=18, hour=19)
      party9 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party9_orders1 = [[66, 100, 1],
                        [67, 100, 0],
                        [68, 100, 1],
                        [69, 100, 0],
                        [70, 100, 1],
                        [71, 100, 0]]
      order_date1 = datetime(year=2013, month=3, day=18, hour=21)
      create_orders(party9, party9_orders1, order_date1)

      # party 10
      party_id = 10
      pro = User.objects.get(email="pro10@gmail.com")
      host = User.objects.get(email="host10@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [72, 73, 74, 75, 76, 77, 78, 79]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=19, hour=19)
      party10 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party10_orders1 = [[72, 100, 1],
                        [73, 100, 0],
                        [74, 100, 1],
                        [75, 100, 0],
                        [76, 100, 1],
                        [77, 100, 0],
                        [78, 100, 1],
                        [79, 100, 0]]
      order_date1 = datetime(year=2013, month=3, day=19, hour=21)
      create_orders(party10, party10_orders1, order_date1)

      # party 11
      party_id = 11
      pro = User.objects.get(email="pro11@gmail.com")
      host = User.objects.get(email="host11@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [81, 82, 83, 84, 85, 86, 87, 88]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=20, hour=19)
      party11 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party11_orders1 = [[81, 100, 0],
                        [82, 100, 1],
                        [83, 100, 0],
                        [84, 100, 1],
                        [85, 100, 0],
                        [86, 100, 1],
                        [87, 100, 0],
                        [88, 100, 1]]
      order_date1 = datetime(year=2013, month=3, day=20, hour=21)
      create_orders(party11, party11_orders1, order_date1)

      # party 12
      party_id = 12
      pro = User.objects.get(email="pro12@gmail.com")
      host = User.objects.get(email="host12@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [89, 90, 91, 92, 93, 94, 95, 96, 97]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=3, day=25, hour=19)
      party12 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party12_orders1 = [[89, 100, 0],
                        [90, 100, 1],
                        [91, 100, 0],
                        [92, 100, 1],
                        [93, 100, 0],
                        [94, 100, 1],
                        [95, 100, 0],
                        [96, 100, 1],
                        [97, 100, 0]]
      order_date1 = datetime(year=2013, month=3, day=25, hour=21)
      create_orders(party12, party12_orders1, order_date1)

      # party 13
      party_id = 13
      pro = User.objects.get(email="pro11@gmail.com")
      host = User.objects.get(email="host11@gmail.com")

      street1 = "30%d Franklin St." % party_id
      city = "Cambridge"
      state = "MA"
      zipcode = "02139"
      title = "Host %d's Party" % party_id
      description = "Great Awesome Party %d" % party_id
      # invite attendees
      attendees = []
      for i in [97, 98, 99, 100, 101, 102, 103]:
        attendees.append("taster%d@gmail.com" % i)
      event_date = datetime(year=2013, month=4, day=13, hour=19)
      party12 = create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date)

      # create orders
      party12_orders1 = [[97, 100, 0],
                        [98, 100, 0],
                        [99, 100, 1],
                        [100, 100, 1],
                        [101, 100, 1],
                        [102, 100, 1],
                        [103, 100, 1]]
      order_date1 = datetime(year=2013, month=4, day=13, hour=21)
      create_orders(party12, party12_orders1, order_date1)

      non_party_orders = [
              [37, 13, 100, 0, datetime(year=2013, month=3, day=14, hour=21)],
              [57, 13, 100, 0, datetime(year=2013, month=3, day=17, hour=21)],
              [80, 13, 100, 1, datetime(year=2013, month=3, day=19, hour=21)],
              [2, 1, 100, 1, datetime(year=2013, month=4, day=10, hour=21)],
              [4, 1, 100, 1, datetime(year=2013, month=4, day=10, hour=21)],
              [6, 1, 100, 1, datetime(year=2013, month=4, day=10, hour=21)],
              [8, 2, 100, 1, datetime(year=2013, month=4, day=11, hour=21)],
              [10, 2, 100, 1, datetime(year=2013, month=4, day=11, hour=21)],
              [12, 3, 100, 1, datetime(year=2013, month=4, day=12, hour=21)],
              [14, 3, 100, 1, datetime(year=2013, month=4, day=12, hour=21)],
              [16, 3, 100, 1, datetime(year=2013, month=4, day=12, hour=21)],
              [18, 3, 100, 1, datetime(year=2013, month=4, day=12, hour=21)],
              [20, 4, 100, 1, datetime(year=2013, month=4, day=13, hour=21)],
              [22, 4, 100, 1, datetime(year=2013, month=4, day=13, hour=21)],
              [24, 4, 100, 1, datetime(year=2013, month=4, day=13, hour=21)],
              [26, 4, 100, 1, datetime(year=2013, month=4, day=13, hour=21)],
              [28, 1, 100, 1, datetime(year=2013, month=4, day=14, hour=21)],
              [30, 2, 100, 1, datetime(year=2013, month=4, day=14, hour=21)],
              [32, 5, 100, 1, datetime(year=2013, month=4, day=14, hour=21)],
              [34, 5, 100, 1, datetime(year=2013, month=4, day=14, hour=21)],
              [36, 5, 100, 1, datetime(year=2013, month=4, day=14, hour=21)],
              [38, 6, 100, 1, datetime(year=2013, month=4, day=15, hour=21)],
              [40, 6, 100, 1, datetime(year=2013, month=4, day=15, hour=21)],
              [42, 6, 100, 1, datetime(year=2013, month=4, day=15, hour=21)],
              [44, 6, 100, 1, datetime(year=2013, month=4, day=15, hour=21)],
              [46, 6, 100, 1, datetime(year=2013, month=4, day=15, hour=21)],
              [48, 7, 100, 1, datetime(year=2013, month=4, day=16, hour=21)],
              [50, 7, 100, 1, datetime(year=2013, month=4, day=16, hour=21)],
              [52, 7, 100, 1, datetime(year=2013, month=4, day=16, hour=21)],
              [54, 7, 100, 1, datetime(year=2013, month=4, day=16, hour=21)],
              [56, 7, 100, 1, datetime(year=2013, month=4, day=16, hour=21)],
              [58, 8, 100, 1, datetime(year=2013, month=4, day=18, hour=21)],
              [60, 8, 100, 1, datetime(year=2013, month=4, day=18, hour=21)],
              [62, 8, 100, 1, datetime(year=2013, month=4, day=18, hour=21)],
              [64, 8, 100, 1, datetime(year=2013, month=4, day=18, hour=21)],
              [66, 9, 100, 1, datetime(year=2013, month=4, day=18, hour=21)],
              [68, 9, 100, 1, datetime(year=2013, month=4, day=18, hour=21)],
              [70, 9, 100, 1, datetime(year=2013, month=4, day=18, hour=21)],
              [72, 10, 100, 1, datetime(year=2013, month=4, day=19, hour=21)],
              [74, 10, 100, 1, datetime(year=2013, month=4, day=19, hour=21)],
              [76, 10, 100, 1, datetime(year=2013, month=4, day=19, hour=21)],
              [78, 10, 100, 1, datetime(year=2013, month=4, day=19, hour=21)],
              [80, 13, 100, 1, datetime(year=2013, month=4, day=19, hour=21)],
              [82, 11, 100, 1, datetime(year=2013, month=4, day=20, hour=21)],
              [84, 11, 100, 1, datetime(year=2013, month=4, day=20, hour=21)],
              [86, 11, 100, 1, datetime(year=2013, month=4, day=20, hour=21)],
              [88, 11, 100, 1, datetime(year=2013, month=4, day=20, hour=21)],
              [90, 12, 100, 1, datetime(year=2013, month=4, day=25, hour=21)],
              [92, 12, 100, 1, datetime(year=2013, month=4, day=25, hour=21)],
              [94, 12, 100, 1, datetime(year=2013, month=4, day=25, hour=21)],
              [96, 12, 100, 1, datetime(year=2013, month=4, day=25, hour=21)],
              [2, 1, 100, 1, datetime(year=2013, month=5, day=10, hour=21)],
              [4, 1, 100, 1, datetime(year=2013, month=5, day=10, hour=21)],
              [6, 1, 100, 1, datetime(year=2013, month=5, day=10, hour=21)],
              [8, 2, 100, 1, datetime(year=2013, month=5, day=11, hour=21)],
              [10, 2, 100, 1, datetime(year=2013, month=5, day=11, hour=21)],
              [12, 3, 100, 1, datetime(year=2013, month=5, day=12, hour=21)],
              [14, 3, 100, 1, datetime(year=2013, month=5, day=12, hour=21)],
              [16, 3, 100, 1, datetime(year=2013, month=5, day=12, hour=21)],
              [18, 3, 100, 1, datetime(year=2013, month=5, day=12, hour=21)],
              [20, 4, 100, 1, datetime(year=2013, month=5, day=13, hour=21)],
              [22, 4, 100, 1, datetime(year=2013, month=5, day=13, hour=21)],
              [24, 4, 100, 1, datetime(year=2013, month=5, day=13, hour=21)],
              [26, 4, 100, 1, datetime(year=2013, month=5, day=13, hour=21)],
              [99, 11, 100, 1, datetime(year=2013, month=5, day=13, hour=21)],
              [100, 11, 100, 1, datetime(year=2013, month=5, day=13, hour=21)],
              [101, 11, 100, 1, datetime(year=2013, month=5, day=13, hour=21)],
              [102, 11, 100, 1, datetime(year=2013, month=5, day=13, hour=21)],
              [103, 11, 100, 1, datetime(year=2013, month=5, day=13, hour=21)],
              [28, 1, 100, 1, datetime(year=2013, month=5, day=14, hour=21)],
              [30, 2, 100, 1, datetime(year=2013, month=5, day=14, hour=21)],
              [32, 5, 100, 1, datetime(year=2013, month=5, day=14, hour=21)],
              [34, 5, 100, 1, datetime(year=2013, month=5, day=14, hour=21)],
              [36, 5, 100, 1, datetime(year=2013, month=5, day=14, hour=21)],
              [38, 6, 100, 1, datetime(year=2013, month=5, day=15, hour=21)],
              [40, 6, 100, 1, datetime(year=2013, month=5, day=15, hour=21)],
              [42, 6, 100, 1, datetime(year=2013, month=5, day=15, hour=21)],
              [44, 6, 100, 1, datetime(year=2013, month=5, day=15, hour=21)],
              [46, 6, 100, 1, datetime(year=2013, month=5, day=15, hour=21)],
              [48, 7, 100, 1, datetime(year=2013, month=5, day=16, hour=21)],
              [50, 7, 100, 1, datetime(year=2013, month=5, day=16, hour=21)],
              [52, 7, 100, 1, datetime(year=2013, month=5, day=16, hour=21)],
              [54, 7, 100, 1, datetime(year=2013, month=5, day=16, hour=21)],
              [56, 7, 100, 1, datetime(year=2013, month=5, day=16, hour=21)],
              [58, 8, 100, 1, datetime(year=2013, month=5, day=18, hour=21)],
              [60, 8, 100, 1, datetime(year=2013, month=5, day=18, hour=21)],
              [62, 8, 100, 1, datetime(year=2013, month=5, day=18, hour=21)],
              [64, 8, 100, 1, datetime(year=2013, month=5, day=18, hour=21)],
              [66, 9, 100, 1, datetime(year=2013, month=5, day=18, hour=21)],
              [68, 9, 100, 1, datetime(year=2013, month=5, day=18, hour=21)],
              [70, 9, 100, 1, datetime(year=2013, month=5, day=18, hour=21)],
              [72, 10, 100, 1, datetime(year=2013, month=5, day=19, hour=21)],
              [74, 10, 100, 1, datetime(year=2013, month=5, day=19, hour=21)],
              [76, 10, 100, 1, datetime(year=2013, month=5, day=19, hour=21)],
              [78, 10, 100, 1, datetime(year=2013, month=5, day=19, hour=21)],
              [80, 13, 100, 1, datetime(year=2013, month=5, day=19, hour=21)],
              [82, 11, 100, 1, datetime(year=2013, month=5, day=20, hour=21)],
              [84, 11, 100, 1, datetime(year=2013, month=5, day=20, hour=21)],
              [86, 11, 100, 1, datetime(year=2013, month=5, day=20, hour=21)],
              [88, 11, 100, 1, datetime(year=2013, month=5, day=20, hour=21)],
              [90, 12, 100, 1, datetime(year=2013, month=5, day=25, hour=21)],
              [92, 12, 100, 1, datetime(year=2013, month=5, day=25, hour=21)],
              [94, 12, 100, 1, datetime(year=2013, month=5, day=25, hour=21)],
              [96, 12, 100, 1, datetime(year=2013, month=5, day=25, hour=21)],
      ]
      create_non_party_orders(non_party_orders)

    def test_order_from_another_pro(self):
      """
        Test the case where party is organized by a pro other than the linked pro
      """
      pass
