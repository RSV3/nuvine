from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import RequestContext,   Context, Template
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
  # Need to add these info
  #[Order Summary] 

  #[Shipping and Billing Info]

  message_template = Template("""

  Hey {{ customer }},


  Thank you for choosing Vinely! 

  Your order {{ order_id }} has been received and 
  you should expect your delicious surprise in 7 - 10 business days. 
  Remember, someone 21 years or older must be available to receive your order.


  Keep an eye on your inbox over the next few days, as we will be sending further shipping information.

  You can check the status of your order at:

    http://{{ host_name }}{% url order_complete order_id %}

  Happy Tasting!

  The Vinely Team

  """)

  c = RequestContext(request, {"customer": order.receiver.first_name if order.receiver.first_name else "Vinely Fan", 
              "host_name": request.get_host(),
              "order_id": order_id}) 

  message = message_template.render(c)
  subject = 'Your Vinely order was placed successfully!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))

  # notify the receiver that the order has been received 
  from_email = 'sales@vinely.com'
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
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))

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

  c = RequestContext( request, {"order": order,
              "host_name": request.get_host()})

  message = message_template.render(c)

  receiver_email = order.receiver.email
  sender_email = order.ordered_by.email

  recipients = [receiver_email]
  if sender_email != receiver_email:
    recipients.append(sender_email)

  subject = 'Order ID: %s has been shipped!' % order.order_id
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))

  msg = EmailMultiAlternatives(subject, message, 'sales@vinely.com', recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_host_vinely_party_email(request, pro=None):

  message_template = Template("""

  Hey {{ pro_first_name }}!

  Guess what? (Drumroll, please.) Someone in your area would like to be a Socializer 
  at a Vinely Taste Party! Please follow up ASAP to help set up an event date, 
  make recommendations, and answer any possible questions.

  Name: {{ first_name }} {{ last_name }}

  Email Address: {{ email }} 

  {% if phone %}
  Phone: {{ phone }}
  {% endif %}

  If you have any questions, please contact a Vinely Care Specialist at 
  (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 

  Your Tasteful Friends,

  - The Vinely Team
 
  """)

  profile = request.user.get_profile()

  c = RequestContext( request, {"first_name": request.user.first_name if request.user.first_name else "Vinely", 
              "last_name": request.user.last_name if request.user.last_name else "Fan",
              "email": request.user.email,
              "pro_first_name": pro.first_name if pro else "Care Specialist",
              "phone": profile.phone,
              "host_name": request.get_host()})

  message = message_template.render(c)

  # new engagement interest
  recipients = ['sales@vinely.com']
  if pro:
    recipients.append(pro.email)

  # notify interest in hosting to Vinely Pro or vinely sales 
  subject = 'A Vinely Taste Party is ready to be scheduled'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))

  # update our DB that there was repeated interest
  interest, created = EngagementInterest.objects.get_or_create(user=request.user, engagement_type=EngagementInterest.ENGAGEMENT_CHOICES[0][0])
  if not created:
    interest.update_time()
  else:
    msg = EmailMultiAlternatives(subject, message, request.user.email, recipients)
    msg.attach_alternative(html_msg, "text/html")
    msg.send()

  # return text message for display
  return message 

def send_know_pro_party_email(request):

  message_template = Template("""

  Hey {{ socializer_first_name }}!

  We're thrilled about your interest in hosting a Vinely Taste Party!  

  Since you already have a Vinely Pro in mind, they will soon be in contact to set a date and time.

  If you haven't heard anything in 48 hours, please contact a Vinely Care Specialist at:

    (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 


  Your Tasteful Friends,

  - The Vinely Team

  """)

  c = RequestContext( request, {"socializer_first_name": request.user.first_name if request.user.first_name else "Vinely Socializer"})

  message = message_template.reander(c)

  subject = 'Get the party started with Vinely'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))

  msg = EmailMultiAlternatives(subject, message, request.user.email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_not_in_area_party_email(request):

  message_template = Template("""

  Hey {{ socializer_first_name }}!

  We have some good news and some bad news.

  The Bad News: Vinely does not currently operate in your area. (Bummer, right?)

  The Good News: Your interest in Vinely is super important to us! So much, in fact, 
  that when we do expand to your area, you'll be the very first to know.

  If you have any questions, please contact a Vinely Care Specialist at: 

    (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 


  Your Tasteful Friends,

  - The Vinely Team

  """)

  c = RequestContext( request, {"socializer_first_name": request.user.first_name if request.user.first_name else "Vinely Socializer"})

  message = message_template.reander(c)

  subject = 'Thanks for your interest in becoming a Vinely Socializer!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))

  msg = EmailMultiAlternatives(subject, message, request.user.email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


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

  c = RequestContext( request, {"socializer_first_name": party.socializer.first_name if party.socializer.first_name else "Superb Socializer", 
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
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))

  msg = EmailMultiAlternatives(subject, message, request.user.email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_party_invitation_email(request, party_invite):
  """ 
    individual invitation e-mail
  """

  message_template = Template("""

  What's a Vinely Party? Think of it as learning through drinking.  It's part wine tasting.
  Part personality test.  And part... well... party.

  The wines you'll sample will give us an idea of your personal taste. The flavors you enjoy 
  and the ones you could do without. After sipping, savoring, and rating each wine, we'll 
  assign you one of six Vinely Personalities. Then, we'll be able to send wines perfectly 
  paired to your taste - right to your doorstep.

    Party: "{{ party.title }}"
    {% if party.description %}{{ party.description }}{% endif %}
    Date: {{ party.event_date|date:"F j, o" }}
    Time: {{ party.event_date|date:"g:i A" }}
    Location: {{ party.address.full_text }}


  Will you attend? You know you want to! RSVP by (5 days prior to event). Better yet, don't wait! 

  <div class="email-rsvp-button">
    <a href="http://{{ host_name }}{% url party_rsvp party.id %}">RSVP Now</a>
  </div>

  <div class="signature">
    <img src="{{ STATIC_URL }}img/vinely_logo_signature.png">
  </div>
  Your Tasteful Friends,

  - The Vinely Team

  """)

  c = RequestContext( request, {"party": party_invite.party,
              "invite_socializer_name": "%s %s"%(request.user.first_name, request.user.last_name),
              "invite_socializer_email": request.user.email,
              "host_name": request.get_host()})
  message = message_template.render(c)

  # send out party invitation e-mail 
  subject = "%s has invited you to a Vinely Taste Party!" % party_invite.party.host.first_name if party_invite.party.host.first_name else "Your Favorite Socializer"

  recipients = [party_invite.invitee.email]  
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'header': 'Good wine and good times await', 
                                                            'message': message}))

  msg = EmailMultiAlternatives(subject, message, 'support@vinely.com', recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def distribute_party_invites_email(request, invitation_sent):

  message_template = Template("""

  What's a Vinely Party? Think of it as learning through drinking.  It's part wine tasting.
  Part personality test.  And part... well... party.

  The wines you'll sample will give us an idea of your personal taste. The flavors you enjoy 
  and the ones you could do without. After sipping, savoring, and rating each wine, we'll 
  assign you one of six Vinely Personalities. Then, we'll be able to send wines perfectly 
  paired to your taste - right to your doorstep.

    Party: "{{ party.title }}"
    {% if party.description %}{{ party.description }}{% endif %}
    Date: {{ party.event_date|date:"F j, o" }}
    Time: {{ party.event_date|date:"g:i A" }}
    Location: {{ party.address.full_text }}

  {% if custom_message %}
  {{ custom_message }}
  {% endif %}

  Will you attend? You know you want to! RSVP by (5 days prior to event). Better yet, don't wait! 

  <div class="email-rsvp-button">
    <a href="http://{{ host_name }}{% url party_rsvp party.id %}">RSVP Now</a>
  </div>

  <div class="signature">
    <img src="{{ STATIC_URL }}img/vinely_logo_signature.png">
  </div>
  Your Tasteful Friends,

  - The Vinely Team


  """)

  c = RequestContext( request, {"party": invitation_sent.party,
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
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'header': 'Good wine and good times await', 
                                                            'message': message}))

  msg = EmailMultiAlternatives(subject, message, 'support@vinely.com', recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  return msg
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

  c = RequestContext( request, {"contact_request": contact_request})
  message = message_template.render(c)

  # send e-mail to notify about contact request
  subject = "URGENT: Request for information"
  recipients = ['sales@vinely.com']
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))

  msg = EmailMultiAlternatives(subject, message, contact_request.email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()
