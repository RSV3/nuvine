from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import RequestContext,   Context, Template
from django.template.loader import render_to_string
from django.contrib.auth.models import Group

from main.models import Order, EngagementInterest, MyHost, PartyInvite
from support.models import Email
from accounts.models import VinelyProAccount
from datetime import tzinfo, timedelta
from cms.models import Section

ZERO = timedelta(0)

class UTC(tzinfo):
  """UTC"""

  def utcoffset(self, dt):
    return ZERO

  def tzname(self, dt):
    return "UTC"

  def dst(self, dt):
    return ZERO

def if_supplier(user):
  """
    Used in user_passes_test decorator to check if user is a supplier
  """
  if user:
    return user.groups.filter(name="Supplier").count() > 0
  return False
  
def if_pro(user):
  """
    Used in user_passes_test decorator to check if user is a supplier
  """
  if user:
    return user.groups.filter(name="Vinely Pro").count() > 0
  return False
  
def send_order_confirmation_email(request, order_id):

  order = Order.objects.get(order_id=order_id)

  if order.fulfill_status > 0:
    # return if already processing since e-mail has already been sent
    return
  
  receiver_email = order.receiver.email
  sender_email = order.ordered_by.email

  recipients = [receiver_email]
  if sender_email != receiver_email:
    recipients.append(sender_email)

  # TODO: if the order contains a tasting kit, notify the party pro
  # Need to add these info
  #[Order Summary] 

  #[Shipping and Billing Info]
  
  template = Section.objects.get(template__key='order_confirmation_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content('\n\n') if x]))

  subject = 'Your Vinely order was placed successfully!'
  from_email = 'Vinely Order <order@vinely.com>'
  recipients = [order.receiver.email]
  
  c = RequestContext( request, {"customer": order.receiver.first_name if order.receiver.first_name else "Vinely Fan", 
              "host_name": request.get_host(),
              "order_id": order_id,
              "title": subject})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request,
      {'title': subject, 'message': html_message, 'host_name': request.get_host()}
    ))


  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # notify the receiver that the order has been received 
  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  # formulate e-mail to the supplier
  content = """
  {% load static %}
  Dear Supplier,

  Customer ({{ customer }}) has completed an order. Please process the order as soon as possible.  You can check the status of their order at:

    http://{{ host_name }}{% url supplier_edit_order order_id %}

  {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

  Your Tasteful Friends,
  
  - The Vinely Team

  """

  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  subject = 'Order ID: %s has been submitted!'%order_id
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, 
    {'title': subject, 'message': html_message, 'host_name': request.get_host()}))

  from_email = 'Vinely <welcome@vinely.com>'
  recipients = ['fulfillment@vinely.com']

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # notify the supplier that an order has been received
  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  order.fulfill_status = 1
  order.save()

def send_order_shipped_email(request, order):
  
  template = Section.objects.get(template__key='order_shipped_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"order": order,
              "host_name": request.get_host()})
  txt_message = txt_template.render(c)

  c.update({'sig':True})
  html_message = html_template.render(c)

  receiver_email = order.receiver.email
  sender_email = order.ordered_by.email

  recipients = [receiver_email]
  if sender_email != receiver_email:
    recipients.append(sender_email)

  subject = 'Order ID: %s has been shipped!' % order.order_id
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, 
    {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Order <order@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, bcc=['fulfillment@vinely.com'])
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_host_vinely_party_email(request, user, pro=None):
  
  template = Section.objects.get(template__key='host_vinely_party_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))
  
  profile = user.get_profile()

  c = RequestContext( request, {"first_name": user.first_name if user.first_name else "Vinely", 
                                "last_name": user.last_name if user.last_name else "Fan",
                                "email": user.email,
                                "pro_first_name": pro.first_name if pro else "Care Specialist",
                                "phone": profile.phone,
                                "host_name": request.get_host(),
                                "zipcode":user.get_profile().zipcode})

  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)

  # new engagement interest
  recipients = ['sales@vinely.com']
  if pro:
    recipients.append(pro.email)

  # notify interest in hosting to Vinely Pro or vinely sales 
  subject = 'A Vinely Taste Party is ready to be scheduled'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = ('Vinely Party <%s>' % user.email)

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # update our DB that there was repeated interest
  interest, created = EngagementInterest.objects.get_or_create(user=user, engagement_type=EngagementInterest.ENGAGEMENT_CHOICES[0][0])
  if not created:
    interest.update_time()
  else:
    msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
    msg.attach_alternative(html_msg, "text/html")
    msg.send()

  # return text message for display
  return txt_message 

def send_new_party_scheduled_email(request, party):

  template = Section.objects.get(template__key='new_party_scheduled_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x])) #Template("<pre>%s</pre>" % content)

  profile = request.user.get_profile()

  c = RequestContext( request, {"host_first_name": party.host.first_name if party.host.first_name else "Superb Host", 
              "pro_email": request.user.email,
              "pro_phone": profile.phone,
              "pro_first_name": request.user.first_name,
              "pro_last_name": request.user.last_name,
              "party": party,
              "host_name": request.get_host()})

  txt_message = txt_template.render(c)
  c.update({'sig':True})
  html_message = html_template.render(c)

  # notify about scheduled party
  recipients = [party.host.email]
  subject = 'Your Vinely Party has been Scheduled!'  
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = ('Vinely Party <%s>' % request.user.email)

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def distribute_party_invites_email(request, invitation_sent):
  
  template = Section.objects.get(template__key='distribute_party_invites_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))
  rsvp_date = invitation_sent.party.event_date - timedelta(days=5)

  c = RequestContext( request, {"party": invitation_sent.party,
              "custom_message": invitation_sent.custom_message,
              "invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name) if request.user.first_name else "Friendly Host",
              "invite_host_email": request.user.email,
              "host_name": request.get_host(), "rsvp_date": rsvp_date,
              "plain":True})
  txt_message = txt_template.render(c)
  c.update({'sig':True, 'plain':False})
  html_message = html_template.render(c)

  recipients = []
  for guest in invitation_sent.guests.all():
    recipients.append(guest.email)

  # send out party invitation e-mail 
  subject = invitation_sent.custom_subject 
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'header': 'Good wine and good times await', 
                                                            'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Party Invite <welcome@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  return msg

def send_rsvp_thank_you_email(request):

  template = Section.objects.get(template__key='rsvp_thank_you_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"first_name": request.user.first_name} )
  txt_message = txt_template.render(c)
  c.update({'sig':True, 'plain':False})
  html_message = html_template.render(c)

  recipients = [ request.user.email ]

  # send out party invitation e-mail 
  subject = 'Thanks for the RSVP!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'header': 'Good wine and good times await', 
                                                            'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Confirmation <welcome@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()
  return msg
   
def send_contact_request_email(request, contact_request):
  """
    E-mail sent when someone fills out a contact request
  """
  
  template = Section.objects.get(template__key='contact_request_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"contact_request": contact_request})
  txt_message = txt_template.render(c)
  html_message = html_template.render(c)

  # send e-mail to notify about contact request
  subject = "URGENT: Request for information"
  recipients = ['sales@vinely.com']
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = ('Vinely <%s>' % contact_request.email)

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_pro_assigned_notification_email(request, pro, host):
  
  template = Section.objects.get(template__key='pro_assigned_notification_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"host_user": host, "pro_user": pro})
  txt_message = txt_template.render(c)
  c.update({'sig':True})
  html_message = html_template.render(c)

  # send e-mail to notify about contact request
  subject = "Congratulations! Vinely Pro has been assigned to you."
  recipients = [host.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = "Vinely Update <care@vinely.com>"

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, bcc=['care@vinely.com'])
  msg.attach_alternative(html_msg, "text/html")
  msg.send()  

def send_mentor_assigned_notification_email(request, mentee, mentor):
  
  template = Section.objects.get(template__key='mentor_assigned_notification_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"mentee": mentee, "mentor": mentor})
  txt_message = txt_template.render(c)
  c.update({'sig':True})
  html_message = html_template.render(c)

  # send e-mail to notify about contact request
  subject = "Congratulations! Vinely Mentor has been assigned to you."
  recipients = [mentee.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = "Vinely Update <care@vinely.com>"

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, bcc=['care@vinely.com'])
  msg.attach_alternative(html_msg, "text/html")
  msg.send() 

def send_mentee_assigned_notification_email(request, mentor, mentee):
  
  template = Section.objects.get(template__key='mentee_assigned_notification_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"mentor": mentor, "mentee": mentee})
  txt_message = txt_template.render(c)
  c.update({'sig':True})
  html_message = html_template.render(c)

  # send e-mail to notify about contact request
  subject = "Congratulations! Vinely Mentee has been assigned to you."
  recipients = [mentor.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = "Vinely Update <care@vinely.com>"

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, bcc=['care@vinely.com'])
  msg.attach_alternative(html_msg, "text/html")
  msg.send() 

##############################################################################
# Utility methods for finding out user relations and party relations
##############################################################################

def first_party(user):
  """
    returns string of the date of the party that the user first participated
  """
  invites = PartyInvite.objects.filter(invitee=user).order_by('invited_timestamp')
  if invites.exists():
    return invites[0].invited_timestamp.strftime('%m/%d/%Y') 
  else:
    return "No party yet"

def my_host(user):

  ps_group = Group.objects.get(name="Vinely Pro")
  ph_group = Group.objects.get(name="Vinely Host")
  tas_group = Group.objects.get(name='Vinely Taster')

  # first host that invited me 
  invitation = PartyInvite.objects.filter(invitee=user).order_by('invited_timestamp')
  if invitation.exists():
    return invitation[0].party.host

  return None 

def my_pro(user):

  ps_group = Group.objects.get(name="Vinely Pro")
  ph_group = Group.objects.get(name="Vinely Host")
  tas_group = Group.objects.get(name='Vinely Taster')

  if ps_group in user.groups.all():
    # I am the pro
    return user, user.get_profile()

  if ph_group in user.groups.all():
      mypros = MyHost.objects.filter(host=user, pro__isnull=False).order_by('-timestamp')
      if mypros.exists():
        pro = mypros[0].pro
        pro_profile = mypros[0].pro.get_profile()
        return pro, pro_profile
  elif tas_group in user.groups.all():
    # find pro and host who invited first
    invitation = PartyInvite.objects.filter(invitee=user).order_by('invited_timestamp')
    if invitation.exists():
      host = invitation[0].party.host
      # find pro that arranged party for my host 
      mypros = MyHost.objects.filter(host=host).order_by('-timestamp')
      if mypros.exists():
        pro = mypros[0].pro
        pro_profile = mypros[0].pro.get_profile()
        return pro, pro_profile

  # no parties, so no pros
  return None, None

from django.db.models import Sum
from main.models import *
from datetime import timedelta, datetime
def calculate_host_credit(host):
  # get all past parties hosted by host
  today = datetime.now(tz=UTC())
  host_parties = Party.objects.filter(host = host, event_date__lt = today)
  
  # only calculate credit if they have hosted a party
  if host_parties.count() == 0:
    return 0
  
  total_orders = 0
  for party in host_parties:
    # get orders made <= 7 days after party
    party_window = party.event_date + timedelta(days=7)
    
    orders = Order.objects.filter(cart__party = party, order_date__lte = party_window)
    # exclude orders made by host
    orders = orders.exclude(ordered_by = host)
    # should not be tasting kit
    orders = orders.exclude(cart__items__product__category = Product.PRODUCT_TYPE[0][0])
    #print 'party date', party.event_date, 'window', party_window
    #print 'order date', [(party_window - x.order_date) for x in orders]
    #print 'order date', [(x.ordered_by.email, x.cart.party.event_date) for x in orders]
    aggregate = orders.aggregate(total = Sum('cart__items__total_price'))
    total_orders += aggregate['total'] if aggregate['total'] else 0
  
  # sales < 399 = 0 credit
  # 400 - 599 = 40
  # 600 - 799 = 60
  # 800 - 999 = 90
  # 1000-1199 = 120
  # 1200-1399 = 150
  credit = 20 * host_parties.count()
  
  total = int(total_orders + 1)
  for cost in range(400, total, 200):
    if cost == 400:
      credit += 40
    elif cost > 800:
      credit += 30
    else:
      credit += 20
  
  return credit

from accounts.models import SubscriptionInfo
from main.models import OrganizedParty
def calculate_pro_commission(pro):
  '''
  returns tuple (<pro_commission from own parties>, <commission from mentee parties>)
  '''
  # TODO: How to exclude orders made using vinely host credits
  # 10% for one-time purchase basic level
  # 12.5% for subscription, superior, divine

  # 1. Calculate for pro's parties
  org_parties = OrganizedParty.objects.filter(pro = pro)
  parties = [p.party for p in org_parties]
  basic_total = other_total = freq_total = mentee_total = 0
  for party in parties:
    orders = Order.objects.filter(cart__party = party)
    # exclude taste kits
    orders = orders.exclude(cart__items__product__category = Product.PRODUCT_TYPE[0][0])
    
    # get one-time basic orders
    one_time_basic = orders.filter(cart__items__frequency = SubscriptionInfo.FREQUENCY_CHOICES[0][0], cart__items__price_category__in = [5, 6])
    # get one-time divine, superior
    one_time_other = orders.filter(cart__items__frequency = SubscriptionInfo.FREQUENCY_CHOICES[0][0], cart__items__price_category__in = [7, 8, 9, 10])
    # get frequency buys
    freq_orders = orders.filter(cart__items__frequency__in = [1,2,3])

    basic_aggr = one_time_basic.aggregate(total=Sum('cart__items__total_price'))
    basic_total += basic_aggr['total'] if basic_aggr['total'] else 0

    other_aggr = one_time_other.aggregate(total = Sum('cart__items__total_price'))
    other_total += other_aggr['total'] if other_aggr['total'] else 0

    freq_aggr = freq_orders.aggregate(total = Sum('cart__items__total_price'))
    freq_total += freq_aggr['total'] if freq_aggr['total'] else 0

  # 2. calculate for mentee's parties
  # 5% of mentee's retail sales if within 120 days of party
  mentees = User.objects.filter(userprofile__mentor = pro)  
  org_parties = OrganizedParty.objects.filter(pro__in = mentees)
  parties = [p.party for p in org_parties]

  for party in parties:
    # get orders made within 120 days after party
    party_window = party.event_date + timedelta(days=90)
    orders = Order.objects.filter(order_date__lte = party_window, cart__party = party)
    # exclude taste kits
    orders = orders.exclude(cart__items__product__category = Product.PRODUCT_TYPE[0][0])
    aggr = orders.aggregate(total = Sum('cart__items__total_price'))
    mentee_total += aggr['total'] if aggr['total'] else 0

  # returns tuple (<pro_commission from own parties>, <commission from mentee parties>)
  return ((0.1 * float(basic_total)) + (0.125 * float(other_total)) + (0.125 * float(freq_total)), # pro commissions
           (0.05 * float(mentee_total)) # mentee commissions
          ) 

import re
def generate_pro_account_number():
  '''
  Generate a new account number for a pro in the format VP#####A
  '''
  #TODO: avoid race condition
  max = 99999
  accounts_to_ignore = ['VP00090A', 'VP00091A', 'VP00092A', 'VP00093A', 'VP00094A', 'VP00095A', 'VP00096A', 'VP00097A', 'VP00098A', 'VP00099A']
  latest = VinelyProAccount.objects.exclude(account_number__in = accounts_to_ignore).order_by('-account_number')[:1]
  if latest.exists():
    prefix = 'VP' # latest[:2]
    account = latest[0].account_number
    suffix = account[7:] # last chars(s) after number
    num = int(re.findall('\d+', account)[0])
    if num == max:
      last = suffix[-1]
      if last == 'Z':
        suffix += 'A'
        num = 1
      else:
        num = 1
        suffix = suffix[:-1] + chr(ord(last)+1)
    else:
      num += 1
    acc_num = '%s%s%s' % (prefix, '%0*d' % (5, num), suffix)
  else:
    acc_num = 'VP00100A'
  return acc_num