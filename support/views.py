from django.shortcuts import render_to_response, get_object_or_404, render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.conf import settings

from support.models import Email, WineInventory, Wine
from main.models import Party, PartyInvite, Order, MyHost, SelectedWine
from personality.models import WineRatingData
from accounts.models import SubscriptionInfo

from support.forms import InventoryUploadForm
from main.utils import my_pro
from datetime import datetime
import csv


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

  for user in User.objects.all():
    data = {}
    data['ID'] = user.id
    data['First Name'] = user.first_name
    data['Last Name'] = user.last_name
    data['E-mail'] = user.email
    profile = user.get_profile()
    data['Zipcode'] = profile.zipcode
    data['Wine Personality'] = profile.wine_personality.name
    data['Date of Birth'] = profile.dob.strftime('%m/%d/%Y') if profile.dob else None
    subscription = SubscriptionInfo.objects.filter(user=user).ordered_by('-updated_datetime')
    if subscription.exists():
      data['Subscription Frequency'] = subscription.get_frequency_display()
      data['Subscription Quantity'] = subscription.get_quantity_display()
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
    data['First Name'] = user.first_name
    data['Last Name'] = user.last_name
    data['E-mail'] = user.email
    profile = user.get_profile()
    data['Zipcode'] = profile.zipcode
    data['Wine Personality'] = profile.wine_personality.name
    data['Date of Birth'] = profile.dob.strftime('%m/%d/%Y') if profile.dob else None
    subscription = SubscriptionInfo.objects.filter(user=user).order_by('-updated_datetime')
    if subscription.exists():
      data['Subscription Frequency'] = subscription.get_frequency_display()
      data['Subscription Quantity'] = subscription.get_quantity_display()
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
  for user in User.objects.all():
    pass
    # export user profile
    # export current subscription information
    # export wine rating data
    # export pro

    # TODO: export party information

    # TODO: export orders

  return render_to_response("support/view_users.html", data, context_instance=RequestContext(request))


@staff_member_required
def view_parties(request):
  for party in Party.objects.all():
    pass
    # export user profile
    # export current subscription information
    # export wine personality
    # export pro
    # export host

    # TODO: export party information


  return render_to_response("support/view_parties.html", data, context_instance=RequestContext(request))


@staff_member_required
def update_wine_inventory(request):

  # present a form to upload wine data

  # after upload, show the wine that have been uploaded and current inventory
  import xlrd

  form = InventoryUploadForm(request.POST or None, request.FILES or None)
  if form.is_valid():
    upload_info = form.save()

    file_name = upload_info.inventory_file.name
    print "Uploaded filename:", file_name

    from boto.s3.connection import S3Connection

    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

    bucket = conn.lookup(settings.AWS_STORAGE_BUCKET_NAME)
    # access the S3 file for processing
    key = bucket.get_key('/media/%s' % file_name)

    key.get_contents_to_filename("inventory_excel.xlsx")
    workbook = xlrd.open_workbook("inventory_excel.xlsx")

    worksheet = workbook.sheet_by_name('Sheet1')

    num_rows = worksheet.nrows - 1
    curr_row = -1

    total_wines = 0
    total_wine_types = 0
    while curr_row < num_rows:
      curr_row += 1
      row = worksheet.row(curr_row)
      # TODO: create wine inventory

      if row[0].ctype is 2:
        print "Inventory ID: %d" % int(row[0].value)
        if row[1].value and row[2].value and row[3].value and row[4].value and row[5].value:
          if Wine.objects.filter(sku=row[3].value).exists():
            wine = Wine.objects.get(sku=row[3].value)
          else:
            wine = Wine(name=row[1].value,
                              year=row[2].value,
                              sku=row[3].value,
                              vinely_category=row[4].value)
            wine.save()

          inv, created = WineInventory.objects.get_or_create(wine=wine)
          if created:
            inv.on_hand = row[5].value
          else:
            inv.on_hand += row[5].value

          inv.save()

          total_wines += row[5].value
          total_wine_types += 1

    messages.success(request, "%s wine types and %s wine bottles have been uploaded to inventory." % (total_wine_types, total_wines))
    return HttpResponseRedirect(reverse("support:view_orders"))

  return render(request, "support/update_wine_inventory.html")


@staff_member_required
def view_orders(request, order_id=None):

  # show orders that have not been fulfilled
  orders = Order.objects.filter(fulfill_status__lt=Order.FULFILL_CHOICES[5][0])

  # could search and filter by order_id
  for o in orders:
    receiver = o.receiver
    # get wine personality
    personality = receiver.get_profile().wine_personality
    rating_data = WineRatingData.objects.filter(user=receiver)

    # algorithm based on the rating data

    # for testing, fulfill with only wine 1
    w1 = Wine.objects.get(sku="VW200101-1")
    u3 = User.objects.get(email="attendee3@example.com")
    inv1 = WineInventory.objects.get(wine=w1)

    if o.receiver == u3:
      # couldn't fulfill
      o.fulfill_status = Order.FULFILL_CHOICES[5][0]
    else:
      # fulfilled wine
      num_slots = o.num_slots()
      wine_added = 0
      for i in range(num_slots):
        if inv1.on_hand > 0:
          wine_selected = SelectedWine(order=o, wine=w1)
          wine_selected.save()
          inv1.on_hand -= 1
          inv1.save()
          wine_added += 1

      # if not enough wines we cannot fulfill
      if wine_added == num_slots:
        o.fulfill_status = Order.FULFILL_CHOICES[6][0]
      else:
        o.fulfill_status = Order.FULFILL_CHOICES[5][0]

    o.save()

  # shows the orders and the wines that have been assigned to it

  # allows one to modify the orders

  # POST: update the wine assignment by running the algorithm

  return render(request, "support/view_orders.html")


@staff_member_required
def edit_order(request, order_id):

  # GET: show details of order, show the ratings on past orders

  # POST: save the order modification

  return render(request, "support/edit_order.html")

@staff_member_required
def download_ready_orders(request):

  # check that the orders are all approved

  # download to csv

  # update those downloaded into completed orders

  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=vinely_ready_orders.csv'

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
def view_past_orders(request, order_id=None):

  data = {}

  if order_id:
    form = RateWineForm(request.POST or None)
    if form.is_valid():
      form.save()

    # GET: show details of the order
  else:
    # show the completed orders
    fulfilled_orders = Order.objects.filter(fulfill_status__gte=Order.FULFILL_CHOICES[6][0])

    data['fulfilled_orders'] = fulfilled_orders

  # allow search of an order, so we can enter rating

  return render(request, "support/view_past_orders.html")

