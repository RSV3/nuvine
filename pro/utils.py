from django.contrib.auth.models import User
from django.utils import timezone

from main.models import OrganizedParty, Party, PartyInvite, Product, LineItem, Cart, Order
from accounts.models import Address, CreditCard

from datetime import timedelta


def create_party(pro, host, street1, city, state, zipcode, title, description, attendees, event_date=None):

  address = Address.objects.create(street1=street1,
                                    city=city,
                                    state=state,
                                    zipcode=zipcode
                                    )

  if event_date:
    party = Party.objects.create(host=host, title=title, description=description,
                              address=address, event_date=event_date)
  else:
    party = Party.objects.create(host=host, title=title, description=description,
                              address=address, event_date=timezone.now() + timedelta(days=10))   

  OrganizedParty.objects.create(pro=pro, party=party)

  # invite people
  for att in attendees:
    PartyInvite.objects.create(party=party, invitee=User.objects.get(email=att), response=PartyInvite.RESPONSE_CHOICES[3][0],
                        invited_timestamp=timezone.now(), response_timestamp=timezone.now())

  return party


def create_orders(party, order_mapping, order_date=None):
  """
    :param order_mapping: contains list of [taster id, order amount, order_type]
    :param order_type: 0 if one time and 1 if VIP
  """
  prod4 = Product.objects.get(name="6 Bottles")

  for order_request in order_mapping:
    # there's order
    item = LineItem(product=prod4, price_category=LineItem.PRICE_TYPE[13][0], quantity=2, frequency=order_request[3], total_price=order_request[2])
    item.save()

    taster = User.objects.get(email="taster%d@gmail.com" % order_request[0])
    pro = User.objects.get(email="pro%d@gmail.com" % order_request[1])

    taster_profile = taster.get_profile()
    taster_profile.current_pro = pro
    taster_profile.save()

    credit_card = CreditCard(nick_name=taster.email, card_number='4111111111111111',
                              exp_month=12, exp_year=15, verification_code='333',
                              billing_zipcode='02139')
    credit_card.save()

    # add item to cart
    cart = Cart(user=taster, receiver=taster, party=party)
    cart.save()
    cart.items.add(item)

    # create order from cart
    shipping_address = Address(street1="%d Dana St. Apt. %d" % (order_request[0], order_request[0]),
                                city="Cambridge",
                                state="MA",
                                zipcode="02139")
    shipping_address.save()

    order = Order(ordered_by=taster, receiver=taster, cart=cart, 
      shipping_address=shipping_address, credit_card=credit_card, fulfill_status=1, carrier=1)
    order.save()

    order.assign_new_order_id()
    if order_date:
      order.order_date = order_date
    order.save()

    cart = order.cart
    cart.status = Cart.CART_STATUS_CHOICES[5][0]
    cart.save()

  print '%d new orders created' % Order.objects.all().count()


def create_non_party_orders(non_party_orders):
  """
    add orders that were ordered post party
  """

  prod4 = Product.objects.get(name="6 Bottles")

  for order_request in non_party_orders:
    # [94, 12, 100, 1, datetime(year=2013, month=5, day=25, hour=21)] 
    # there's order
    item = LineItem(product=prod4, price_category=LineItem.PRICE_TYPE[13][0], quantity=2, frequency=order_request[3], total_price=order_request[2])
    item.save()

    # pro
    linked_pro = User.objects.get(email="pro%d@gmail.com" % order_request[1])
    credit_pro = linked_pro
    taster = User.objects.get(email="taster%d@gmail.com" % order_request[0])

    taster_profile = taster.get_profile()
    taster_profile.current_pro = linked_pro
    taster_profile.save()

    credit_card = CreditCard(nick_name=taster.email, card_number='4111111111111111',
                              exp_month=12, exp_year=15, verification_code='333',
                              billing_zipcode='02139')
    credit_card.save()

    # party is the last party they attended
    party_invitations = PartyInvite.objects.filter(invitee=taster, response_timestamp__lt=timezone.now()).order_by('-response_timestamp')
    party = None
    if party_invitations.exists():
      party = party_invitations[0].party
    if party and party.event_date > timezone.now() - timedelta(days=7):
      # less than 7 days at the party so credit the party pro
      credit_pro = OrganizedParty.objects.get(party=party).pro
    else:
      # just make the purchase part of linked pro
      if order_request[3]:
        past_orders = Order.objects.filter(receiver=taster).order_by('-order_date')
        # it's a VIP order, check this person's last order and assign the party to that order
        if past_orders.exists():
          last_order = Order.objects.filter(receiver=taster).order_by('-order_date')[0]
          if last_order.is_vip():
            party = last_order.cart.party
        #else:
          # there's no VIP so just save this order as new VIP and credit to current linked Pro
      #else:
        # it's a one time order so pro is the linked pro

    # if no party it goes to the linked pro
    # if VIP it goes to the pro who organized party
    # if new VIP order it goes to the linked pro

    # add item to cart
    cart = Cart(user=taster, receiver=taster, party=party)
    cart.save()
    cart.items.add(item)

    # create order from cart
    shipping_address = Address(street1="%d Dana St. Apt. %d" % (order_request[0], order_request[0]),
                                city="Cambridge",
                                state="MA",
                                zipcode="02139")
    shipping_address.save()

    order = Order(ordered_by=taster, receiver=taster, cart=cart, 
      shipping_address=shipping_address, credit_card=credit_card, fulfill_status=1, carrier=1)
    order.save()

    order.assign_new_order_id()
    if order_request[4]:
      order.order_date = order_request[4]
    order.save()

    cart = order.cart
    cart.status = Cart.CART_STATUS_CHOICES[5][0]

    cart.save()

  print '%d new orders created' % Order.objects.all().count()

