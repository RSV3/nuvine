from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from support.models import Email
from main.models import Party, PartyInvite, Order, MyHost
from accounts.models import SubscriptionInfo
from main.utils import my_pro
from datetime import datetime
import csv
#import xlwt

@staff_member_required
def list_emails(request):

  data = {}

  emails = Email.objects.all()

  data["emails"] = emails

  return render_to_response("support/list_emails.html", data, context_instance=RequestContext(request))

@staff_member_required
def view_email(request, email_id):

  email = get_object_or_404(Email, pk=email_id)

  return HttpResponse(email.html) 

@staff_member_required
def download_users(request):
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=vinely_users.csv'

  fieldnames = ['ID', 'First Name', 'Last Name', 'E-mail', 'Zipcode', 'Wine Personality', 
                'Date of Birth', 'Subscription Frequency', 'Subscription Quantity', 'Member Since', 'Vinely Pro']
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
    try:
      subscription = SubscriptionInfo.objects.get(user=user)
      data['Subscription Frequency'] = subscription.get_frequency_display() 
      data['Subscription Quantity'] = subscription.get_quantity_display()
    except SubscriptionInfo.DoesNotExist:
      data['Subscription Frequency'] = None 
      data['Subscription Quantity'] = None 
    data['Member Since'] = user.date_joined.strftime('%m/%d/%Y')
    pro = my_pro(user)
    if pro[0]:
      data['Vinely Pro'] = pro[0].email 
    else:
      data['Vinely Pro'] = pro[0]

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

  fieldnames = ['ID', 'Order ID', 'Ordered By', 'Receiver', 'Items', 'Total Price', 
                        'Shipping Address', 'Order Date']

  # most recent orders first
  for order in Order.objects.all().order_by('-order_date'):
    data = {}
    data['ID'] = order.id
    data['Order ID'] = order.order_id
    data['Ordered By'] = "%s %s (%s)" % (order.ordered_by.first_name, order.ordered_by.last_name, order.ordered_by.email)
    data['Receiver'] = "%s %s (%s)" % (order.ordered_by.first_name, order.ordered_by.last_name, order.ordered_by.email)
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
def view_orders(request):
  for order in Order.objects.all():
    pass

    # export user profile
    # export current subscription information
    # export wine personality 
    # export pro


    # TODO: export orders

  return render_to_response("support/view_orders.html", data, context_instance=RequestContext(request)) 