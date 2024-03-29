from django.shortcuts import render_to_response, get_object_or_404, render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.conf import settings
from django.forms.formsets import formset_factory
from django.db import transaction
from django.views.decorators.http import require_POST
from django.utils import timezone

from django_tables2 import RequestConfig

from support.models import Email, WineInventory, TastingKitInventory
from support.tables import WineInventoryTable, OrderTable, PastOrderTable, TastingInventoryTable, UserTable, \
                            OrderHistoryTable, PartyTable, PartyAttendeesTable

from main.models import Party, PartyInvite, Order, MyHost, SelectedWine, CustomizeOrder, SelectedTastingKit

from personality.models import WineRatingData, Wine, TastingKit
from accounts.models import SubscriptionInfo
from main.forms import AttendeesTable
from support.forms import InventoryUploadForm, SelectedWineRatingForm, ChangeFulfillStatusForm, SelectTastingKitForm, \
                        RefundForm
from main.utils import my_pro, calculate_host_credit
from datetime import datetime
import csv
import stripe

import logging

log = logging.getLogger(__name__)


@staff_member_required
def admin_index(request):
  """
    Shows list of things admin can do
  """

  data = {}

  return render_to_response("support/admin_index.html", data, context_instance=RequestContext(request))


@staff_member_required
def manage_subscriptions(request):

  data = {}

  subscription_ids = []
  for user_id in SubscriptionInfo.objects.exclude(frequency__in=[0, 9]).filter(quantity__gt=0).values_list('user', flat=True).distinct():
    user = User.objects.get(id=user_id)

    # need to work with only the latest subscription info per user
    subscription = SubscriptionInfo.objects.filter(user=user).order_by('-updated_datetime')[0]
    subscription_ids.append(subscription.id)

  subscriptions = SubscriptionInfo.objects.filter(id__in=subscription_ids).order_by('next_invoice_date')

  page_num = request.GET.get('p', 1)
  paginator = Paginator(subscriptions, 20)
  try:
    page = paginator.page(page_num)
  except:
    page = paginator.page(1)

  data['page_count'] = paginator.num_pages
  data['page'] = page
  data['subscriptions'] = page.object_list

  return render_to_response("support/manage_subscriptions.html", data, context_instance=RequestContext(request))


@staff_member_required
def list_emails(request):

  data = {}

  search_email = request.GET.get('email', '').strip()
  if search_email:
    emails = Email.objects.filter(recipients__contains=search_email).order_by('-timestamp')
  else:
    emails = Email.objects.all().order_by('-timestamp')
  page_num = request.GET.get('p', 1)
  paginator = Paginator(emails, 20)
  try:
    page = paginator.page(page_num)
  except:
    page = paginator.page(1)

  data['search_email'] = search_email
  data['page_count'] = paginator.num_pages
  data['page'] = page
  data['emails'] = page.object_list

  return render_to_response("support/list_emails.html", data, context_instance=RequestContext(request))


@staff_member_required
def view_email(request, email_id):

  email = get_object_or_404(Email, pk=email_id)

  return HttpResponse(email.html)


@staff_member_required
def download_users(request):
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=vinely_users.csv'

  fieldnames = ['ID', 'First Name', 'Last Name', 'E-mail', 'Zipcode', 'Date of Birth',
                'Subscription Frequency', 'Subscription Quantity', 'Member Since',
                'Vinely Pro', 'Wine Personality',
                'Wine 1 Overall', 'Wine 1 Sweet', 'Wine 1 Sweet DNL', 'Wine 1 Weight', 'Wine 1 Weight DNL',
                'Wine 1 Texture', 'Wine 1 Texture DNL', 'Wine 1 Sizzle', 'Wine 1 Sizzle DNL',
                'Wine 2 Overall', 'Wine 2 Sweet', 'Wine 2 Sweet DNL', 'Wine 2 Weight', 'Wine 2 Weight DNL',
                'Wine 2 Texture', 'Wine 2 Texture DNL', 'Wine 2 Sizzle', 'Wine 2 Sizzle DNL',
                'Wine 3 Overall', 'Wine 3 Sweet', 'Wine 3 Sweet DNL', 'Wine 3 Weight', 'Wine 3 Weight DNL',
                'Wine 3 Texture', 'Wine 3 Texture DNL', 'Wine 3 Sizzle', 'Wine 3 Sizzle DNL',
                'Wine 4 Overall', 'Wine 4 Sweet', 'Wine 4 Sweet DNL', 'Wine 4 Weight', 'Wine 4 Weight DNL',
                'Wine 4 Texture', 'Wine 4 Texture DNL', 'Wine 4 Sizzle', 'Wine 4 Sizzle DNL',
                'Wine 5 Overall', 'Wine 5 Sweet', 'Wine 5 Sweet DNL', 'Wine 5 Weight', 'Wine 5 Weight DNL',
                'Wine 5 Texture', 'Wine 5 Texture DNL', 'Wine 5 Sizzle', 'Wine 5 Sizzle DNL',
                'Wine 6 Overall', 'Wine 6 Sweet', 'Wine 6 Sweet DNL', 'Wine 6 Weight', 'Wine 6 Weight DNL',
                'Wine 6 Texture', 'Wine 6 Texture DNL', 'Wine 6 Sizzle', 'Wine 6 Sizzle DNL']

  writer = csv.DictWriter(response, fieldnames)

  writer.writeheader()

  from accounts.models import UserProfile
  for user in User.objects.all():

    try:
      prof = user.get_profile()
    except UserProfile.DoesNotExist:
      continue

    data = {}
    data['ID'] = user.id
    data['First Name'] = user.first_name.encode('utf-8')
    data['Last Name'] = user.last_name.encode('utf-8')
    data['E-mail'] = user.email
    profile = user.get_profile()
    data['Zipcode'] = profile.zipcode
    data['Wine Personality'] = profile.wine_personality.name
    data['Date of Birth'] = profile.dob.strftime('%m/%d/%Y') if profile.dob else None
    subscription = SubscriptionInfo.objects.filter(user=user).order_by('-updated_datetime')
    if subscription.exists():
      data['Subscription Frequency'] = subscription[0].get_frequency_display()
      data['Subscription Quantity'] = subscription[0].get_quantity_display()
    else:
      data['Subscription Frequency'] = None
      data['Subscription Quantity'] = None
    data['Member Since'] = user.date_joined.strftime('%m/%d/%Y')
    pro = my_pro(user)
    if pro[0]:
      data['Vinely Pro'] = pro[0].email
    else:
      data['Vinely Pro'] = pro[0]

    for wine_id in [1, 2, 3, 4, 5, 6]:
      try:
        rating = WineRatingData.objects.get(user=user, wine__id=wine_id)
        data['Wine %d Overall' % wine_id] = rating.overall
        data['Wine %d Sweet' % wine_id] = rating.sweet
        data['Wine %d Sweet DNL' % wine_id] = rating.sweet_dnl
        data['Wine %d Weight' % wine_id] = rating.weight
        data['Wine %d Weight DNL' % wine_id] = rating.weight_dnl
        data['Wine %d Texture' % wine_id] = rating.texture
        data['Wine %d Texture DNL' % wine_id] = rating.texture_dnl
        data['Wine %d Sizzle' % wine_id] = rating.sizzle
        data['Wine %d Sizzle DNL' % wine_id] = rating.sizzle_dnl
      except WineRatingData.DoesNotExist:
        data['Wine %d Overall' % wine_id] = 0
        data['Wine %d Sweet' % wine_id] = 0
        data['Wine %d Sweet DNL' % wine_id] = 0
        data['Wine %d Weight' % wine_id] = 0
        data['Wine %d Weight DNL' % wine_id] = 0
        data['Wine %d Texture' % wine_id] = 0
        data['Wine %d Texture DNL' % wine_id] = 0
        data['Wine %d Sizzle' % wine_id] = 0
        data['Wine %d Sizzle DNL' % wine_id] = 0

    writer.writerow(data)

  return response


@staff_member_required
def download_users_from_party(request, party_id):
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=vinely_users.csv'

  fieldnames = ['ID', 'First Name', 'Last Name', 'E-mail', 'Zipcode', 'Date of Birth',
                'Subscription Frequency', 'Subscription Quantity', 'Member Since',
                'Vinely Pro', 'Wine Personality',
                'Wine 1 Overall', 'Wine 1 Sweet', 'Wine 1 Sweet DNL', 'Wine 1 Weight', 'Wine 1 Weight DNL',
                'Wine 1 Texture', 'Wine 1 Texture DNL', 'Wine 1 Sizzle', 'Wine 1 Sizzle DNL',
                'Wine 2 Overall', 'Wine 2 Sweet', 'Wine 2 Sweet DNL', 'Wine 2 Weight', 'Wine 2 Weight DNL',
                'Wine 2 Texture', 'Wine 2 Texture DNL', 'Wine 2 Sizzle', 'Wine 2 Sizzle DNL',
                'Wine 3 Overall', 'Wine 3 Sweet', 'Wine 3 Sweet DNL', 'Wine 3 Weight', 'Wine 3 Weight DNL',
                'Wine 3 Texture', 'Wine 3 Texture DNL', 'Wine 3 Sizzle', 'Wine 3 Sizzle DNL',
                'Wine 4 Overall', 'Wine 4 Sweet', 'Wine 4 Sweet DNL', 'Wine 4 Weight', 'Wine 4 Weight DNL',
                'Wine 4 Texture', 'Wine 4 Texture DNL', 'Wine 4 Sizzle', 'Wine 4 Sizzle DNL',
                'Wine 5 Overall', 'Wine 5 Sweet', 'Wine 5 Sweet DNL', 'Wine 5 Weight', 'Wine 5 Weight DNL',
                'Wine 5 Texture', 'Wine 5 Texture DNL', 'Wine 5 Sizzle', 'Wine 5 Sizzle DNL',
                'Wine 6 Overall', 'Wine 6 Sweet', 'Wine 6 Sweet DNL', 'Wine 6 Weight', 'Wine 6 Weight DNL',
                'Wine 6 Texture', 'Wine 6 Texture DNL', 'Wine 6 Sizzle', 'Wine 6 Sizzle DNL']

  writer = csv.DictWriter(response, fieldnames)

  writer.writeheader()

  party = get_object_or_404(Party, pk=party_id)

  for user_dict in PartyInvite.objects.filter(party=party).values('invitee'):
    data = {}
    user = User.objects.get(id=user_dict["invitee"])
    data['ID'] = user.id
    data['First Name'] = user.first_name.encode('utf-8')
    data['Last Name'] = user.last_name.encode('utf-8')
    data['E-mail'] = user.email
    profile = user.get_profile()
    data['Zipcode'] = profile.zipcode
    data['Wine Personality'] = profile.wine_personality.name
    data['Date of Birth'] = profile.dob.strftime('%m/%d/%Y') if profile.dob else None
    subscription = SubscriptionInfo.objects.filter(user=user).order_by('-updated_datetime')
    if subscription.exists():
      data['Subscription Frequency'] = subscription[0].get_frequency_display()
      data['Subscription Quantity'] = subscription[0].get_quantity_display()
    else:
      data['Subscription Frequency'] = None
      data['Subscription Quantity'] = None
    data['Member Since'] = user.date_joined.strftime('%m/%d/%Y')
    pro = my_pro(user)
    if pro[0]:
      data['Vinely Pro'] = pro[0].email
    else:
      data['Vinely Pro'] = pro[0]

    for wine_id in [1, 2, 3, 4, 5, 6]:
      try:
        rating = WineRatingData.objects.get(user=user, wine__id=wine_id)
        data['Wine %d Overall' % wine_id] = rating.overall
        data['Wine %d Sweet' % wine_id] = rating.sweet
        data['Wine %d Sweet DNL' % wine_id] = rating.sweet_dnl
        data['Wine %d Weight' % wine_id] = rating.weight
        data['Wine %d Weight DNL' % wine_id] = rating.weight_dnl
        data['Wine %d Texture' % wine_id] = rating.texture
        data['Wine %d Texture DNL' % wine_id] = rating.texture_dnl
        data['Wine %d Sizzle' % wine_id] = rating.sizzle
        data['Wine %d Sizzle DNL' % wine_id] = rating.sizzle_dnl
      except WineRatingData.DoesNotExist:
        data['Wine %d Overall' % wine_id] = 0
        data['Wine %d Sweet' % wine_id] = 0
        data['Wine %d Sweet DNL' % wine_id] = 0
        data['Wine %d Weight' % wine_id] = 0
        data['Wine %d Weight DNL' % wine_id] = 0
        data['Wine %d Texture' % wine_id] = 0
        data['Wine %d Texture DNL' % wine_id] = 0
        data['Wine %d Sizzle' % wine_id] = 0
        data['Wine %d Sizzle DNL' % wine_id] = 0

    writer.writerow(data)

  return response


@staff_member_required
def download_parties(request):

  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=vinely_parties.csv'

  fieldnames = ['ID', 'Title', 'Host Name', 'Host E-mail', 'Host Phone', 'Number of Invitees',
                  'Number of Orders', 'Vinely Pro']
  writer = csv.DictWriter(response, fieldnames)

  writer.writeheader()

  today = datetime.today()

  for party in Party.objects.filter(event_date__gte=today).order_by('-event_date'):
    data = {}
    data['ID'] = party.id
    data['Title'] = party.title
    data['Host Name'] = "%s %s" % (party.host.first_name, party.host.last_name)
    data['Host E-mail'] = party.host.email
    data['Host Phone'] = party.phone

    # find total number of items ordered
    total_order = 0
    invites = PartyInvite.objects.filter(party=party)
    for inv in invites:
      total_order += Order.objects.filter(receiver=inv.invitee, order_date__gte=party.event_date).count()
    data['Number of Orders'] = total_order
    host_pro = MyHost.objects.get(host=party.host)
    data['Vinely Pro'] = host_pro.pro.email if host_pro.pro else host_pro.pro

    writer.writerow(data)

  return response


@staff_member_required
def download_orders(request):
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=vinely_orders.csv'

  fieldnames = ['ID', 'Order ID', 'Ordered By', 'Receiver', 'Wine Personality', 'Items', 'Total Price',
                        'Shipping Address', 'Order Date']

  writer = csv.DictWriter(response, fieldnames)

  writer.writeheader()

  # most recent orders first
  for order in Order.objects.all().order_by('-order_date'):
    data = {}
    data['ID'] = order.id
    data['Order ID'] = order.order_id
    data['Ordered By'] = "%s %s (%s)" % (order.ordered_by.first_name, order.ordered_by.last_name, order.ordered_by.email)
    data['Receiver'] = "%s %s (%s)" % (order.receiver.first_name, order.receiver.last_name, order.receiver.email)
    data['Wine Personality'] = order.receiver.get_profile().wine_personality
    data['Items'] = order.cart.items_str()
    data['Total Price'] = order.cart.total()
    data['Shipping Address'] = order.shipping_address
    data['Order Date'] = order.order_date.strftime("%m/%d/%Y")

    writer.writerow(data)

  return response


@staff_member_required
def view_users(request):
  data = {}

  users = User.objects.all().order_by('first_name', 'last_name')

  table = UserTable(users)
  RequestConfig(request, paginate={"per_page": 100}).configure(table)

  data['users_table'] = table

  return render(request, "support/user_overview.html", data)


@staff_member_required
def view_user_details(request, user_id):
  data = {}
  user = get_object_or_404(User, pk=user_id)
  profile = user.get_profile()

  data['user_detail'] = user
  data['profile_detail'] = profile
  data['credit_card'] = profile.stripe_card
  orders = Order.objects.filter(ordered_by=user).select_related().order_by('-id')
  table = OrderHistoryTable(orders, user=user)
  RequestConfig(request, paginate={"per_page": 20}).configure(table)
  data['order_history'] = table
  return render(request, "support/user_detail.html", data)


@staff_member_required
def view_parties(request):
  data = {}
  # user = request.user
  parties = Party.objects.all().select_related().order_by('-event_date')

  table = PartyTable(parties)
  RequestConfig(request, paginate={"per_page": 100}).configure(table)

  data['parties_table'] = table

  return render(request, "support/view_parties.html", data)


@staff_member_required
def view_party_detail(request, party_id):
  user = request.user
  data = {}

  party = get_object_or_404(Party, id=party_id)
  tasters = PartyInvite.objects.filter(party=party).select_related()
  table = PartyAttendeesTable(tasters, user=user, data={'party': party, 'can_add_taster': True, 'can_shop_for_taster': True})
  # table = PartyAttendeesTable(tasters)
  RequestConfig(request, paginate={"per_page": 30}).configure(table)

  data['tasters_table'] = table
  data['party'] = party
  data['host_credit'] = party.host.userprofile.account_credit
  return render(request, "support/view_party_detail.html", data)


@staff_member_required
def wine_inventory(request):

  data = {}

  # present a form to upload wine data

  # after upload, show the wine that have been uploaded and current inventory
  import xlrd

  form = InventoryUploadForm(request.POST or None, request.FILES or None)

  if form.is_valid():
    upload_info = form.save()

    file_name = upload_info.inventory_file.name
    log.info("Uploaded filename: %s" % file_name)

    if settings.MEDIA_URL.startswith("//s3"):
      from boto.s3.connection import S3Connection

      conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

      bucket = conn.lookup(settings.AWS_STORAGE_BUCKET_NAME)
      # access the S3 file for processing
      key = bucket.get_key('/media/%s' % file_name)

      key.get_contents_to_filename("inventory_excel.xlsx")
      workbook = xlrd.open_workbook("inventory_excel.xlsx")
    else:
      # we're dealing with local
      workbook = xlrd.open_workbook(settings.MEDIA_ROOT + file_name)

    try:
      worksheet = workbook.sheet_by_name('Wine DB')

      num_rows = worksheet.nrows - 1
      curr_row = 0
      invalid_rows = []

      total_wines = 0
      total_wine_types = 0

      # if num_rows > 0:
      #   # deactivate all and have them activated again so that wines that are not in
      #   # the uploaded inventory remain deactivated
      #   today = timezone.now()
      #   TastingKit.objects.all().update(active=False, updated=today)
      #   Wine.objects.all().update(active=False, deactivated=today)

      while curr_row < num_rows:
        curr_row += 1
        row = worksheet.row(curr_row)

        # if first column value is a Vinely SKU
        if row[0].value and (row[0].value[0] == 'V' or row[0].value.lower().startswith("tasting")):
          #print "Inventory ID: %s" % row[0].value
          if row[1].value.lower() == 'tk':
            sku = row[0].value
            comment = row[2].value
            name = row[3].value
            on_hand = row[4].value
            price = row[21].value if row[21].value else 0

            # for tasting kit, add to Product database not to Wine database
            if TastingKit.objects.filter(sku=sku).exists():
              tasting_kit = TastingKit.objects.get(sku=sku)
            else:
              tasting_kit = TastingKit(name=name, sku=sku, comment=comment, price=price)

            tasting_kit.active = True
            tasting_kit.updated = timezone.now()
            tasting_kit.save()

            inv, created = TastingKitInventory.objects.get_or_create(tasting_kit=tasting_kit)
            inv.on_hand = on_hand
            inv.save()

            total_wines += on_hand
            total_wine_types += 1

          elif row[1].value and row[3].value and row[4].value and row[5].value and row[6].value:
            sku = row[0].value
            color = row[1].value
            name = row[3].value
            on_hand = row[4].value
            cat_1 = row[5].value
            cat_2 = row[6].value
            # vintage
            year = row[9].value

            brand = row[7].value
            varietal = row[8].value
            region = row[10].value
            alcohol = float(row[11].value) if row[11].value else 0

            cost_per_bottle = row[21].value if row[21].value else 0
            acidity = float(row[13].value) if row[13].value else 0
            ph = float(row[14].value) if row[14].value else 0
            oak = float(row[15].value) if row[15].value else 0
            body = float(row[16].value) if row[16].value else 0
            fruit = float(row[17].value) if row[17].value else 0
            tannin = float(row[18].value) if row[18].value else 0

            sparkling = row[19].value

            color_code = Wine.WINE_COLOR[0][0]
            if 'white' in color.lower():
              color_code = Wine.WINE_COLOR[1][0]
            elif 'rose' in color.lower() or u'ros\xc3' in color.lower():
              color_code = Wine.WINE_COLOR[2][0]

            sparkling = str(sparkling).lower()
            sparkling_code = False
            if 'yes' in sparkling or '1' in sparkling:
              sparkling_code = True

            enclosure = row[20].value.lower() if row[20].value else 'unknown'
            if enclosure == 'unknown':
              enclosure = Wine.ENCLOSURE_CHOICES[0][0]
            elif enclosure == 'screw':
              enclosure = Wine.ENCLOSURE_CHOICES[1][0]
            elif enclosure == 'cork':
              enclosure = Wine.ENCLOSURE_CHOICES[2][0]

            if Wine.objects.filter(sku=sku).exists():
              wine = Wine.objects.get(sku=sku)
            else:
              wine = Wine(name=name,
                                year=year if year else 0,
                                sku=sku,
                                vinely_category=cat_1,
                                vinely_category2=cat_2,
                                brand=brand,
                                varietal=varietal,
                                region=region,
                                alcohol=alcohol,
                                color=color_code,
                                acidity=acidity,
                                ph=ph,
                                oak=oak,
                                body=body,
                                fruit=fruit,
                                tannin=tannin,
                                sparkling=sparkling_code,
                                enclosure=enclosure,
                                price=cost_per_bottle)
            wine.active = True
            wine.updated = timezone.now()
            wine.save()

            inv, created = WineInventory.objects.get_or_create(wine=wine)
            inv.on_hand = on_hand
            inv.save()

            total_wines += on_hand
            total_wine_types += 1
        else:
          invalid_rows.append(curr_row)

      if invalid_rows:
        messages.warning(request, "Rows %s had invalid data" % invalid_rows)

      messages.success(request, "%s wine types and %d wine bottles have been uploaded to inventory." % (total_wine_types, int(total_wines)))
    except xlrd.XLRDError:
      messages.warning(request, "Not a valid inventory file: needs 'Wine DB' sheet.")

  # only return wines from the latest inventory
  latest_kit_inventory = TastingKitInventory.objects.all()  # filter(tasting_kit__active=True)
  tasting_table = TastingInventoryTable(latest_kit_inventory)
  data["tasting_inventory"] = tasting_table

  latest_wine_inventory = WineInventory.objects.all()  # filter(wine__active=True)
  table = WineInventoryTable(latest_wine_inventory)
  data["wine_inventory"] = table
  RequestConfig(request, paginate={"per_page": 25}).configure(table)

  data["form"] = form
  return render(request, "support/wine_inventory.html", data)


def fill_slots_in_order(order, wine_choices, slots_remaining):
  """
    return the vinely_order_id if the order was completely fulfilled
  """
  for wine_id in wine_choices:
    picked_wine = Wine.objects.get(id=wine_id)
    # make sure we are not adding duplicate wines
    if order.cart.items.filter(product__category=0).exists():
      already_ordered = False
    else:
      already_ordered = SelectedWine.objects.filter(order=order, wine=picked_wine).exists()

    if not already_ordered:
      wine_selected = SelectedWine(order=order, wine=picked_wine)
      wine_selected.save()
      # reduce inventory
      wine_inv = picked_wine.wineinventory
      wine_inv.on_hand -= 1
      wine_inv.save()
      slots_remaining -= 1
      if slots_remaining == 0:
        order.fulfill_status = Order.FULFILL_CHOICES[6][0]
        order.save()
        # completely fulfilled
        return slots_remaining, order.vinely_order_id
  # not completely fulfilled
  return slots_remaining, None


@staff_member_required
def fulfill_orders(request, order_id=None):
  data = {}
  fulfilled_orders = []

  orders = Order.objects.filter(fulfill_status__lt=Order.FULFILL_CHOICES[6][0])

  if Wine.objects.all().count() == 0 or WineInventory.objects.filter(on_hand__gt=0).count() == 0:
    messages.warning(request, "No wine in the inventory")
  else:
    # fulfill wine
    for o in orders:
      slots_remaining = o.num_slots
      if slots_remaining == 0:
        continue

      # deal with tasting kits first
      if o.cart.items.filter(product__category=0).exists():
        wine_choices = Wine.objects.filter(is_taste_kit_wine=True, wineinventory__on_hand__gt=0).values_list('id', flat=True)
        slots_remaining, fulfilled_vinely_order_id = fill_slots_in_order(o, wine_choices, slots_remaining)
        if fulfilled_vinely_order_id:
          fulfilled_orders.append(fulfilled_vinely_order_id)
        else:
          o.fulfill_status = Order.FULFILL_CHOICES[5][0]
          o.save()
        continue

      receiver = o.receiver
      # get wine personality and rating data to filter wine
      personality = receiver.get_profile().wine_personality
      like_categories = WineRatingData.objects.filter(user=receiver, overall__gt=3).values_list("wine__number", flat=True)

      # algorithm based on the rating data
      wine_choices = Wine.objects.filter(vinely_category__in=like_categories, wineinventory__on_hand__gt=0, is_taste_kit_wine=False).values_list('id', flat=True)

      # if enough wine in the inventory, fulfill
      # fulfill likes only
      slots_remaining, fulfilled_vinely_order_id = fill_slots_in_order(o, wine_choices, slots_remaining)
      if fulfilled_vinely_order_id:
        fulfilled_orders.append(fulfilled_vinely_order_id)

      if slots_remaining:
        # else find the liked wines from past orders that are in inventory
        liked_past_choices = SelectedWine.objects.filter(order__receiver=receiver, overall_rating__gt=3).values_list('wine', flat=True)

        slots_remaining, fulfilled_vinely_order_id = fill_slots_in_order(o, liked_past_choices, slots_remaining)
        if fulfilled_vinely_order_id:
          fulfilled_orders.append(fulfilled_vinely_order_id)

      if slots_remaining:
        # if not enough likes, then fulfill neutral
        neutral_categories = WineRatingData.objects.filter(user=receiver, overall=3).values_list("wine__number", flat=True)
        neutral_choices = Wine.objects.filter(vinely_category__in=neutral_categories, wineinventory__on_hand__gt=0, is_taste_kit_wine=False).values_list('id', flat=True)

        slots_remaining, fulfilled_vinely_order_id = fill_slots_in_order(o, neutral_choices, slots_remaining)
        if fulfilled_vinely_order_id:
          fulfilled_orders.append(fulfilled_vinely_order_id)

      if slots_remaining:
        # if not enough wines fulfill with neutral from past wines
        neutral_past_choices = SelectedWine.objects.filter(order__receiver=receiver, overall_rating=3).values_list('wine', flat=True)

        slots_remaining, fulfilled_vinely_order_id = fill_slots_in_order(o, neutral_past_choices, slots_remaining)
        if fulfilled_vinely_order_id:
          fulfilled_orders.append(fulfilled_vinely_order_id)

      if slots_remaining > 0:
        # else need to leave for manual review
        o.fulfill_status = Order.FULFILL_CHOICES[5][0]
        o.save()

  if not orders.exists():
    messages.warning(request, "No pending orders are currently in the queue.")

  if fulfilled_orders:
    messages.success(request, "Fullfilled orders: %s" % fulfilled_orders)

  return HttpResponseRedirect(reverse("support:view_orders"))


@staff_member_required
def view_orders(request, order_id=None):

  """
    order_id is used to filter the orders list

    one should be able to click the order and update wines
  """

  data = {}

  # show orders that have not been fulfilled
  if order_id:
    # show particular order
    orders = Order.objects.filter(id=order_id).select_related()
  else:
    orders = Order.objects.all().select_related()

  if not orders.exists():
    messages.warning(request, "No live orders are currently in the queue.")

  # shows the orders and the wines that have been assigned to it
  table = OrderTable(orders)
  RequestConfig(request, paginate={"per_page": 100}).configure(table)

  data["orders"] = table

  return render(request, "support/view_orders.html", data)


@staff_member_required
@transaction.commit_on_success
def edit_order(request, order_id):
  """
    Allows one to modify the order

    - wines don't appear even though selected
    - wine names don't appear
  """

  data = {}

  order = get_object_or_404(Order, pk=order_id)

  # if tasting kit, forward to tasting kit fulfillment url
  if order.is_tasting_kit():
    return HttpResponseRedirect(reverse("support:fulfill_taste_kit", args=(order_id,)))

  if order.fulfill_status >= Order.FULFILL_CHOICES[7][0]:
    return HttpResponseRedirect(reverse("support:rate_order", args=(order_id,)))

  # need to get the past orders for this user
  receiver = order.receiver
  past_orders = Order.objects.filter(receiver=receiver)
  past_ratings = SelectedWine.objects.filter(order__in=past_orders).order_by("-timestamp")

  data['order'] = order
  receiver_profile = order.receiver.get_profile()
  data['receiver_profile'] = receiver_profile
  # users that have only ordered taste kits will not have customization record
  customizations = CustomizeOrder.objects.filter(user=order.receiver)
  customization = customizations[0] if customizations.exists() else None
  data['customization'] = customization
  data['past_orders'] = past_orders
  # show the ratings on past orders
  data['past_ratings'] = past_ratings
  data['recurring'] = order.recurring()
  data['product'] = order.quantity_summary()

  order_status_updated = False
  num_slots = order.num_slots

  from support.forms import SelectWineForm

  SelectedWineFormSet = formset_factory(SelectWineForm, extra=num_slots, max_num=num_slots)

  enough_inventory = True
  if request.method == "POST":
    formset = SelectedWineFormSet(request.POST or None)
    # POST: save the order modification
    for form in formset:
      try:
        if form.has_changed() and form.is_valid():
          #print "Form has has_changed"
          selected_wine = form.save(commit=False)
          if 'record_id' in form.cleaned_data and form.cleaned_data['record_id']:
            past_selection = SelectedWine.objects.get(id=form.cleaned_data['record_id'])
            # update inventory
            old_inv = WineInventory.objects.get(wine=past_selection.wine)
            old_inv.on_hand += 1
            old_inv.save()
            new_inv = WineInventory.objects.get(wine=selected_wine.wine)
            if new_inv.on_hand > 0:
              new_inv.on_hand -= 1
              new_inv.save()
            else:
              messages.warning(request, "There are not enough %s in the inventory." % selected_wine.wine)
              enough_inventory = False
            if enough_inventory:
              past_selection.wine = selected_wine.wine
              past_selection.save()
            else:
              past_selection.delete()
          else:
            new_inv = WineInventory.objects.get(wine=selected_wine.wine)
            if new_inv.on_hand > 0:
              new_inv.on_hand -= 1
              new_inv.save()
            else:
              messages.warning(request, "There are not enough %s in the inventory." % selected_wine.wine)
              enough_inventory = False
            if enough_inventory:
              selected_wine.order = order
              selected_wine.save()
      except ValueError:
        continue
    if order.fulfill_status < Order.FULFILL_CHOICES[6][0] and num_slots == SelectedWine.objects.filter(order=order).count():
      order.fulfill_status = Order.FULFILL_CHOICES[6][0]
      order.save()
      # override the currently selected fulfill status
      order_status_updated = True
      messages.success(request, "Wine selection has been completed for order #%s." % order.vinely_order_id)
    elif enough_inventory:
      messages.success(request, "Saved order details.")

  if order_status_updated:
    status_form = ChangeFulfillStatusForm(instance=order)
  else:
    # form for changing fulfill status of the order
    status_form = ChangeFulfillStatusForm(request.POST or None, instance=order)
    if status_form.is_valid():
      status_form.save()

  data['status_change_form'] = status_form

  # show already selected wines
  selected_wines = SelectedWine.objects.filter(order=order)

  initial_data = []
  for w in selected_wines:
    form_data = {}
    form_data['record_id'] = w.id
    form_data['wine'] = w.wine.id
    if customization:
      if customization.wine_mix == 2:
        form_data['color_filter'] = 0
      elif customization.wine_mix == 3:
        form_data['color_filter'] = 1
      form_data['sparkling_filter'] = True if customization.sparkling else False
    form_data['category_filter'] = receiver_profile.find_neutral_wines()
    initial_data.append(form_data)

  for i in range(0, num_slots - len(initial_data)):
    form_data = {}
    if customization:
      if customization.wine_mix == 2:
        form_data['color_filter'] = 0
      elif customization.wine_mix == 3:
        form_data['color_filter'] = 1
      form_data['sparkling_filter'] = True if customization.sparkling else False
    form_data['category_filter'] = receiver_profile.find_neutral_wines()
    initial_data.append(form_data)

  formset = SelectedWineFormSet(initial=initial_data)

  data['formset'] = formset

  return render(request, "support/edit_order.html", data)

@staff_member_required
def fulfill_taste_kit(request, order_id):
  data = {}

  order = get_object_or_404(Order, pk=order_id)

  # need to get the past orders for this user
  receiver = order.receiver
  past_orders = Order.objects.filter(receiver=receiver)
  past_ratings = SelectedWine.objects.filter(order__in=past_orders, overall_rating__gt=0).order_by("-timestamp")

  data['order'] = order
  receiver_profile = order.receiver.get_profile()
  data['receiver_profile'] = receiver_profile
  # users that have only ordered taste kits will not have customization record
  customizations = CustomizeOrder.objects.filter(user=order.receiver)
  customization = customizations[0] if customizations.exists() else None
  data['customization'] = customization
  data['past_orders'] = past_orders
  # show the ratings on past orders
  data['past_ratings'] = past_ratings
  data['recurring'] = order.recurring()
  data['product'] = order.quantity_summary()

  order_status_updated = False
  old_taste_kit = None
  tasting_kit_selected = SelectedTastingKit.objects.filter(order=order)
  if tasting_kit_selected.exists():
    select_tasting_kit_form = SelectTastingKitForm(request.POST or None, instance=tasting_kit_selected[0])
    old_taste_kit = tasting_kit_selected[0].tasting_kit
  else:
    select_tasting_kit_form = SelectTastingKitForm(request.POST or None)

  if select_tasting_kit_form.is_valid():
    tasting_kit_selected = select_tasting_kit_form.save(commit=False)
    tasting_kit_selected.order = order
    tasting_kit_selected.save()

    if old_taste_kit != tasting_kit_selected.tasting_kit:
      # update inventory
      if old_taste_kit is not None:
        # restore old taste kit
        old_inventory = TastingKitInventory.objects.get(tasting_kit=old_taste_kit)
        old_inventory.on_hand += order.quantity_summary()
        old_inventory.save()

      new_inventory = TastingKitInventory.objects.get(tasting_kit=tasting_kit_selected.tasting_kit)
      new_inventory.on_hand -= order.quantity_summary()
      new_inventory.save()

    if order.fulfill_status < Order.FULFILL_CHOICES[6][0]:
      order.fulfill_status = Order.FULFILL_CHOICES[6][0]
      order.save()
      # override the currently selected fulfill status
      order_status_updated = True
      messages.success(request, "Tasting Kit has been selected for order #%s." % order.vinely_order_id)
    # need to update order status

  data['select_tasting_kit_form'] = select_tasting_kit_form

  # form for changing fulfill status of the order
  if order_status_updated:
    status_form = ChangeFulfillStatusForm(instance=order)
  else:
    status_form = ChangeFulfillStatusForm(request.POST or None, instance=order)
    if status_form.is_valid():
      status_form.save()

  data['status_change_form'] = status_form

  return render(request, "support/fulfill_taste_kit.html", data)


@staff_member_required
def rate_order(request, order_id):
  data = {}

  try:
    order = Order.objects.filter(fulfill_status__gte=Order.FULFILL_CHOICES[6][0]).get(id=order_id)
  except Order.DoesNotExist:
    raise Http404

  # if tasting kit, forward to tasting kit fulfillment url
  if order.is_tasting_kit():
    messages.warning(request, "This is a Tasting Kit order and there's nothing to be rated.")
    return HttpResponseRedirect(reverse("support:fulfill_taste_kit", args=(order_id,)))

  num_slots = order.num_slots

  data['order'] = order
  receiver_profile = order.receiver.get_profile()
  data['receiver_profile'] = receiver_profile
  customization, created = CustomizeOrder.objects.get_or_create(user=order.receiver)
  data['customization'] = customization
  # raise Exception
  status_form = ChangeFulfillStatusForm(request.POST or None, instance=order)
  if status_form.is_valid():
    status_form.save()

  data['status_change_form'] = status_form

  if num_slots == SelectedWine.objects.filter(order=order).count():
    SelectedWineRatingFormSet = formset_factory(SelectedWineRatingForm, extra=num_slots, max_num=num_slots)
    if request.method == "POST":
      formset = SelectedWineRatingFormSet(request.POST or None)
      if formset.is_valid():
        for form in formset:
          if form.has_changed():
            selected_wine = form.save(commit=False)
            if 'record_id' in form.cleaned_data and form.cleaned_data['record_id']:
              past_selection = SelectedWine.objects.get(id=form.cleaned_data['record_id'])
              past_selection.overall_rating = selected_wine.overall_rating
              past_selection.save()
            else:
              selected_wine.save()

        messages.success(request, "Saved ratings for order ID: %s" % order.vinely_order_id)

      data['formset'] = formset
    else:
      # GET: show details of the order
      initial_data = []
      selected_wines = SelectedWine.objects.filter(order=order)

      for selected_wine in selected_wines:
        form_data = {}
        form_data['order'] = order.id
        form_data['record_id'] = selected_wine.id
        form_data['wine'] = selected_wine.wine.id
        form_data['wine_name'] = selected_wine.wine.name
        form_data['overall_rating'] = selected_wine.overall_rating
        initial_data.append(form_data)

      #print initial_data

      formset = SelectedWineRatingFormSet(initial=initial_data)
      data['formset'] = formset
  else:
    # not emough wines have been selected
    messages.warning(request, "The order is an outdated order or not enough wines have been fulfilled.")

  return render(request, "support/rate_order.html", data)


@staff_member_required
def download_ready_orders_old(request):

  # check that the orders are all approved

  # download to csv

  # update those downloaded into completed orders

  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=vinely_ready_orders.csv'

  fieldnames = ['ID', 'Order ID', 'Ordered By', 'Receiver', 'Wine Personality', 'Items', 'Wine SKU', 'Total Price',
                        'Shipping Address', 'Order Date']

  writer = csv.DictWriter(response, fieldnames)

  writer.writeheader()

  # most recent orders first
  for order in Order.objects.filter(fulfill_status=Order.FULFILL_CHOICES[6][0]).order_by('-order_date'):
    data = {}
    data['ID'] = order.id
    data['Order ID'] = order.order_id
    data['Ordered By'] = "%s %s (%s)" % (order.ordered_by.first_name, order.ordered_by.last_name, order.ordered_by.email)
    data['Receiver'] = "%s %s (%s)" % (order.receiver.first_name, order.receiver.last_name, order.receiver.email)
    data['Wine Personality'] = order.receiver.get_profile().wine_personality
    data['Items'] = order.cart.items_str()
    data['Wine SKU'] = [selected.wine.sku for selected in SelectedWine.objects.filter(order=order)]
    data['Total Price'] = order.cart.total()
    data['Shipping Address'] = order.shipping_address
    data['Order Date'] = order.order_date.strftime("%m/%d/%Y")

    writer.writerow(data)

  return response


@require_POST
@staff_member_required
def download_ready_orders(request):

  # check that the orders are all approved

  # download to csv

  # update those downloaded into completed orders
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=vinely_ready_orders.csv'

  fieldnames = ['Format Version', 'Client Code', 'Order No', 'Invoice Number', 'Onsite', 'License to License', 'Do not reconfigure', 
                        'Force 3-tier', 'Order Type', 'Sub-Club', 'Order Date', 'Courier/Ship Method', 'Courier Tracking No',
                        'Fulfiller', 'Requested Ship Date', 'Compliance ID', 'Age Verification ID', 'Recipient ID',
                        'Recipient First Name', 'Recipient Last Name', 'Recipient Company', 'Recipient Address 1',
                        'Recipient Address 2', 'Recipient City', 'Recipient State', 'Recipient Postal Code',
                        'Recipient Country', 'Recipient Work Phone', 'Recipient Home Phone', 'Recipient Mobile Phone',
                        'Recipient Email', 'Recipient DOB', 'Cutomer ID', 'Customer First Name', 'Customer Last Name',
                        'Customer Company', 'Customer Address 1', 'Customer Address 2', 'Customer City', 'Customer State',
                        'Customer Postal Code', 'Customer Country', 'Customer Work Phone', 'Customer Home Phone',
                        'Customer Mobile Phone', 'Customer Email', 'Customer DOB', 'Credit Card Number',
                        'Credit Card Exp Date', 'Payment Authorization Code', 'Special Instructions',
                        'Gift?', 'Gift Message', 'Shipping Total', 'Handling Fees', 'Discount Amount', 'Insurance (if more than Carrier Std)',
                        'Retail Amt (Products Only)',
                        'Prod 1 Supplier', 'Prod 1 SKU', 'Prod 1 Quantity', 'Prod 1 Name', 'Prod 1 Tax',
                        'Prod 1 Price', 'Prod 1 Alcohol %', 'Prod 1 Weight', 'Prod 1 Inventory Location',
                        'Prod 2 Supplier', 'Prod 2 SKU', 'Prod 2 Quantity', 'Prod 2 Name', 'Prod 2 Tax',
                        'Prod 2 Price', 'Prod 2 Alcohol %', 'Prod 2 Weight', 'Prod 2 Inventory Location',
                        'Prod 3 Supplier', 'Prod 3 SKU', 'Prod 3 Quantity', 'Prod 3 Name', 'Prod 3 Tax',
                        'Prod 3 Price', 'Prod 3 Alcohol %', 'Prod 3 Weight', 'Prod 3 Inventory Location',
                        'Prod 4 Supplier', 'Prod 4 SKU', 'Prod 4 Quantity', 'Prod 4 Name', 'Prod 4 Tax',
                        'Prod 4 Price', 'Prod 4 Alcohol %', 'Prod 4 Weight', 'Prod 4 Inventory Location',
                        'Prod 5 Supplier', 'Prod 5 SKU', 'Prod 5 Quantity', 'Prod 5 Name', 'Prod 5 Tax',
                        'Prod 5 Price', 'Prod 5 Alcohol %', 'Prod 5 Weight', 'Prod 5 Inventory Location',
                        'Prod 6 Supplier', 'Prod 6 SKU', 'Prod 6 Quantity', 'Prod 6 Name', 'Prod 6 Tax',
                        'Prod 6 Price', 'Prod 6 Alcohol %', 'Prod 6 Weight', 'Prod 6 Inventory Location',
                        'Prod 7 Supplier', 'Prod 7 SKU', 'Prod 7 Quantity', 'Prod 7 Name', 'Prod 7 Tax',
                        'Prod 7 Price', 'Prod 7 Alcohol %', 'Prod 7 Weight', 'Prod 7 Inventory Location',
                        'Prod 8 Supplier', 'Prod 8 SKU', 'Prod 8 Quantity', 'Prod 8 Name', 'Prod 8 Tax',
                        'Prod 8 Price', 'Prod 8 Alcohol %', 'Prod 8 Weight', 'Prod 8 Inventory Location',
                        'Prod 9 Supplier', 'Prod 9 SKU', 'Prod 9 Quantity', 'Prod 9 Name', 'Prod 9 Tax',
                        'Prod 9 Price', 'Prod 9 Alcohol %', 'Prod 9 Weight', 'Prod 9 Inventory Location',
                        'Prod 10 Supplier', 'Prod 10 SKU', 'Prod 10 Quantity', 'Prod 10 Name', 'Prod 10 Tax',
                        'Prod 10 Price', 'Prod 10 Alcohol %', 'Prod 10 Weight', 'Prod 10 Inventory Location',
                        'Prod 11 Supplier', 'Prod 11 SKU', 'Prod 11 Quantity', 'Prod 11 Name', 'Prod 11 Tax',
                        'Prod 11 Price', 'Prod 11 Alcohol %', 'Prod 11 Weight', 'Prod 11 Inventory Location',
                        'Prod 12 Supplier', 'Prod 12 SKU', 'Prod 12 Quantity', 'Prod 12 Name', 'Prod 12 Tax',
                        'Prod 12 Price', 'Prod 12 Alcohol %', 'Prod 12 Weight', 'Prod 12 Inventory Location']

  #print "All fields: %s" % len(fieldnames) == 166

  try:
    orders = [int(x) for x in request.POST.getlist("orders")]
    if not orders:
      messages.warning(request, 'You did not select any orders')
      return HttpResponseRedirect(reverse("support:view_orders"))
  except:
    messages.warning(request, 'There was an error in the orders you selected')
    return HttpResponseRedirect(reverse("support:view_orders"))

  writer = csv.DictWriter(response, fieldnames)

  writer.writeheader()

  # most recent orders first
  # for order in Order.objects.filter(fulfill_status=Order.FULFILL_CHOICES[6][0]).order_by('-order_date'):
  for order in Order.objects.filter(id__in=orders, fulfill_status=Order.FULFILL_CHOICES[6][0]).order_by('-order_date'):

    data = {}
    data['Format Version'] = 205
    data['Client Code'] = 'Vinely'
    data['Order No'] = order.vinely_order_id
    data['Order Date'] = order.order_date.strftime("%m/%d/%Y")
    data['Courier/Ship Method'] = 'FEX'
    data['Recipient First Name'] = order.receiver.first_name
    data['Recipient Last Name'] = order.receiver.last_name
    receiver_profile = order.receiver.get_profile()
    data['Recipient Company'] = order.shipping_address.company_co
    data['Recipient Address 1'] = order.shipping_address.street1
    data['Recipient Address 2'] = order.shipping_address.street2
    data['Recipient City'] = order.shipping_address.city
    data['Recipient State'] = order.shipping_address.state
    data['Recipient Postal Code'] = order.shipping_address.zipcode
    data['Recipient Country'] = 'USA'
    data['Recipient Work Phone'] = receiver_profile.work_phone
    data['Recipient Home Phone'] = receiver_profile.phone
    data['Special Instructions'] = receiver_profile.wine_personality

    if order.is_tasting_kit():
      # handle tasting kit order
      selected_taste_kit = SelectedTastingKit.objects.get(order=order)
      data['Prod 1 SKU'] = selected_taste_kit.tasting_kit.sku
      data['Prod 1 Quantity'] = order.quantity_summary()
      data['Prod 1 Name'] = selected_taste_kit.tasting_kit.name
      data['Prod 1 Price'] = selected_taste_kit.tasting_kit.price
    else:

      i = 0
      for selected in SelectedWine.objects.filter(order=order):
        i += 1
        data['Prod %d SKU' % i] = selected.wine.sku
        data['Prod %d Quantity' % i] = 1
        data['Prod %d Name' % i] = selected.wine.name
        data['Prod %d Price' % i] = selected.wine.price
        if i == 12:
          # since its an abnormal order if there are more than 12 bottles
          # and since the order form only supports up to 12 bottles
          break

    order.fulfill_status = Order.FULFILL_CHOICES[7][0]
    order.save()

    writer.writerow(data)

  return response


@staff_member_required
def view_past_orders(request, order_id=None):
  """
    If order_id is valid, then view the order and edit the ratings

    else just show the list
  """

  data = {}

  # show the completed orders
  fulfilled_orders = Order.objects.filter(fulfill_status__gte=Order.FULFILL_CHOICES[7][0]).select_related().order_by("-order_date")

  table = PastOrderTable(fulfilled_orders)
  RequestConfig(request, paginate={"per_page": 100}).configure(table)

  data['fulfilled_orders'] = table

  # allow search of an order, so we can enter rating

  return render(request, "support/view_past_orders.html", data)


@staff_member_required
def user_overview(request):
  '''
  Displays a list of users in the system
  '''
  data = {}

  users = User.objects.all()  # .order_by('')

  table = UserTable(users)
  RequestConfig(request, paginate={"per_page": 100}).configure(table)

  data['users_table'] = table

  return render(request, "support/user_overview.html", data)


@staff_member_required
def refund_order(request, order_id):
  data = {}
  # raise Exception
  order = get_object_or_404(Order, pk=order_id)
  previous_page = request.GET.get('next', reverse('support:view_user_details', args=[order.ordered_by.id]))
  data['previous_page'] = previous_page

  refund_form = RefundForm(request.POST or None, instance=order)
  data['refund_form'] = refund_form
  data['order'] = order

  if refund_form.is_valid():
    order = refund_form.save(commit=False)

    stripe.api_key = settings.STRIPE_SECRET_CA
    inv = stripe.Invoice.retrieve(order.stripe_invoice)
    stripe_charge = stripe.Charge.retrieve(inv.charge)

    try:
      if refund_form.cleaned_data.get('full_refund', False):
        stripe_charge.refund()
        refund_amount = order.cart.total()
      else:
        amount = refund_form.cleaned_data.get('refund_amount', 0)
        if amount > 0:
          stripe_charge.refund(amount=int(amount * 100))
          refund_amount = amount

      order.refund_amount = refund_amount
      order.refund_date = timezone.now()
      order.save()
    except Exception, e:
      # some stripe error
      messages.warning(request, "Stripe Error: %s" % e)
    return HttpResponseRedirect(reverse('support:view_user_details', args=[order.ordered_by.id]))

  return render(request, "support/refund_order_modal.html", data)
