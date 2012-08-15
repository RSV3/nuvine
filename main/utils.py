from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Context, Template
from django.template.loader import render_to_string
from main.models import Order, EngagementInterest
from datetime import tzinfo, timedelta

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

  message_template = Template("""

  Dear {{ customer }},

  Thank you for ordering at Vinely. 

  We will soon be processing your order and you should receive your orders in 7 days. 

  You can check the status of your order at:

    http://{{ host_name }}{% url order_complete order_id %}


  """)

  c = Context({"customer": order.receiver.first_name if order.receiver.first_name else "Valued Customer", 
              "host_name": request.get_host(),
              "order_id": order_id}) 

  message = message_template.render(c)
  subject = 'Order Confirmation from Vinely!'
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  # notify the receiver that the order has been received 
  from_email = 'support@vinely.com'
  msg = EmailMultiAlternatives(subject, message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  # formulate e-mail to the supplier
  order_request_template = Template("""

  Customer ({{ customer }}) has completed an order

  Please process the order as soon as possible 

  You can check the status of their order at:

    http://{{ host_name }}{% url supplier_edit_order order_id %}


  """)

  message = message_template.render(c)
  subject = 'Order ID: %s has been submitted!'%order_id
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  # notify the supplier that an order has been received
  from_email = 'support@vinely.com'
  recipients = ['sales@vinely.com']
  msg = EmailMultiAlternatives(subject, message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  order.fulfill_status = 1
  order.save()

def send_order_shipped_email(request, order):
  message_template = Template("""

  Dear {% if order.receiver.first_name %}{{ order.receiver.first_name }}{% else %}Valued Customer{% endif %},

  Your order has been shipped and you should receive your order in the next 7 days.

  You can check the status of your order at:

    http://{{ host_name }}{% url order_complete order.order_id %}

  """)

  c = Context({"order": order,
              "host_name": request.get_host()})

  message = message_template.render(c)

  receiver_email = order.receiver.email
  sender_email = order.ordered_by.email

  recipients = [receiver_email]
  if sender_email != receiver_email:
    recipients.append(sender_email)

  subject = 'Order ID: %s has been shipped!' % order.order_id
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  msg = EmailMultiAlternatives(subject, message, 'sales@vinely.com', recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_host_vinely_party_email(request, pro=None):

  message_template = Template("""

  Dear Vinely,

  I ({{ first_name }} {{ last_name }}) would like to host a Vinely party.

  Could you please connect me to a Vinely Pro that may help me with this arrangement?

  Please let me know via e-mail at: {{ email }}{% if phone %} or call me at {{ phone }}{% endif %}.

  Look forward to hearing from you soon!

  """)

  profile = request.user.get_profile()

  c = Context({"first_name": request.user.first_name if request.user.first_name else "Unknown", 
              "last_name": request.user.last_name if request.user.last_name else "Name",
              "email": request.user.email,
              "phone": profile.phone ,
              "host_name": request.get_host()})

  message = message_template.render(c)

  # update our DB that there was repeated interest
  interest, created = EngagementInterest.objects.get_or_create(user=request.user, engagement_type=EngagementInterest.ENGAGEMENT_CHOICES[0][0])
  if not created:
    interest.update_time()
  else:
    # new engagement interest
    recipients = ['sales@vinely.com']
    if pro:
      recipients.append(pro.email)

    # notify interest in hosting to Vinely Pro or vinely sales 
    subject = 'I am interested in hosting a Vinely Party!'
    html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

    msg = EmailMultiAlternatives(subject, message, request.user.email, recipients)
    msg.attach_alternative(html_msg, "text/html")
    msg.send()

  return message

def send_new_party_scheduled_email(request, party):

  message_template = Template("""

  Dear {{ socializer_first_name }},

  The following party has been scheduled:

    Party: "{{ party.title }}"
    {% if party.description %}{{ party.description }}{% endif %}
    Date: {{ party.event_date|date:"F j, o" }}
    Time: {{ party.event_date|date:"g:i A" }}


  You can start inviting guests to your party at:

    http://{{ host_name }}{% url party_taster_invite party.id %}
  
  If you have any questions, please contact me via e-mail: {{ pro_email }} {% if pro_phone %}or via phone: {{ pro_phone }}{% endif %} 

  Look forward to seeing you soon!

  Your Vinely Pro {{ pro_first_name }} {{ pro_last_name }}

  """)

  profile = request.user.get_profile()

  c = Context({"socializer_first_name": party.socializer.first_name if party.socializer.first_name else "Superb Socializer", 
              "pro_email": request.user.email,
              "pro_phone": profile.phone,
              "pro_first_name": request.user.first_name,
              "pro_last_name": request.user.last_name,
              "party": party,
              "host_name": request.get_host()})

  message = message_template.render(c)

  # notify about scheduled party
  recipients = [party.socializer.email]
  subject = 'Your Vinely Party has been Scheduled!'  
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  msg = EmailMultiAlternatives(subject, message, request.user.email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_party_invitation_email(request, party_invite):
  """ 
    individual invitation e-mail
  """

  message_template = Template("""

  You have been invited to a Vinely Party by {{ invite_socializer_name }} ({{ invite_socializer_email }}).

    Party: "{{ party.title }}"
    {% if party.description %}{{ party.description }}{% endif %}
    Date: {{ party.event_date|date:"F j, o" }}
    Time: {{ party.event_date|date:"g:i A" }}

  You need RSVP to your party invitation at:

    http://{{ host_name }}{% url party_rsvp party.id %}

  Please do this as soon as possible.  

  Thank you!

  from your Vinely pros

  """)

  c = Context({"party": party_invite.party,
              "invite_socializer_name": "%s %s"%(request.user.first_name, request.user.last_name),
              "invite_socializer_email": request.user.email,
              "host_name": request.get_host()})
  message = message_template.render(c)

  # send out party invitation e-mail 
  subject = "You are invited to a Vinely Party!"
  recipients = [party_invite.invitee.email]  
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  msg = EmailMultiAlternatives(subject, message, 'support@vinely.com', recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def distribute_party_invites_email(request, invitation_sent):

  message_template = Template("""

  You have been invited to a Vinely Party by {{ invite_socializer_name }} ({{ invite_socializer_email }}).

    Party: "{{ party.title }}"
    {% if party.description %}{{ party.description }}{% endif %}
    Date: {{ party.event_date|date:"F j, o" }}
    Time: {{ party.event_date|date:"g:i A" }}
    Location: {{ party.address.full_text }}

  {% if custom_message %}
  {{ custom_message }}
  {% endif %}

  You need RSVP to your party invitation at:

    http://{{ host_name }}{% url party_rsvp party.id %}

  Please do this as soon as possible.  

  Thank you!

  from your Vinely pros

  """)

  c = Context({"party": invitation_sent.party,
              "custom_message": invitation_sent.custom_message,
              "invite_socializer_name": "%s %s"%(request.user.first_name, request.user.last_name) if request.user.first_name else "Friendly Socializer",
              "invite_socializer_email": request.user.email,
              "host_name": request.get_host()})
  message = message_template.render(c)

  recipients = []
  for guest in invitation_sent.guests.all():
    recipients.append(guest.email)

  # send out party invitation e-mail 
  subject = invitation_sent.custom_subject 
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  msg = EmailMultiAlternatives(subject, message, 'support@vinely.com', recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_contact_request_email(request, contact_request):
  """
    E-mail sent when someone fills out a contact request
  """
  message_template = Template("""

  {% if contact_request.first_name %}{{ contact_request.first_name }} {{ contact_request.last_name }}{% else %}Potential Customer{% endif %}, is interested in Vinely.  Please reach out via

    E-mail: {{ contact_request.email }}
    Phone: {{ contact_request.phone }}

  Following message was submitted:

    Subject: {{ contact_request.subject }}

    {{ contact_request.message }}

  """)

  c = Context({"contact_request": contact_request})
  message = message_template.render(c)

  # send e-mail to notify about contact request
  subject = "URGENT: Request for information"
  recipients = ['sales@vinely.com']
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  msg = EmailMultiAlternatives(subject, message, contact_request.email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()
