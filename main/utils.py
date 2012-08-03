from django.core.mail import send_mail
from django.template import Context, Template
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

  # TODO: if the order contains a tasting kit, notify the party specialist

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

  # send out verification e-mail, create a verification code
  send_mail('Order Confirmation from Vinely!', message, 'support@vinely.com', recipients)

  order.fulfill_status = 1
  order.save()

def send_host_vinely_party_email(request, specialist=None):

  message_template = Template("""

  Dear Vinely,

  I ({{ first_name }} {{ last_name }}) would like to host a Vinely party.

  Could you please connect me to a party specialist that may help me with this arrangement?

  Please let me know via e-mail at: {{ email }} or call me at {{ phone }}.

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
    if specialist:
      recipients.append(specialist.email)

    # notify party specialist or vinely sales 
    send_mail('I am interested in hosting a Vinely Party!', message, request.user.email, recipients)

  return message

def send_new_party_scheduled_email(request, party):

  message_template = Template("""

  Dear {{ host_first_name }},

  The following party has been scheduled:

    Party: "{{ party.title }}"
    {% if party.description %}{{ party.description }}{% endif %}
    Date: {{ party.event_date|date:"F j, o" }}
    Time: {{ party.event_date|date:"g:i A" }}


  You can start inviting guests to your party at:

    http://{{ host_name }}{% url party_attendee_invite party.id %}
  
  If you have any questions, please contact me via e-mail: {{ specialist_email }} {% if specialist_phone %}or via phone: {{ specialist_phone }}{% endif %} 

  Look forward to seeing you soon!

  Your party specialist {{ specialist_first_name }} {{ specialist_last_name }}

  """)

  profile = request.user.get_profile()

  c = Context({"host_first_name": party.host.first_name if party.host.first_name else "Superb Host", 
              "specialist_email": request.user.email,
              "specialist_phone": profile.phone,
              "specialist_first_name": request.user.first_name,
              "specialist_last_name": request.user.last_name,
              "party": party,
              "host_name": request.get_host()})

  message = message_template.render(c)

  recipients = [party.host.email]

  # notify party host that your party has been scheduled 
  send_mail('Your Vinely Party has been Scheduled!', message, request.user.email, recipients)

def send_party_invitation_email(request, party_invite):
  """ 
    individual invitation e-mail
  """

  message_template = Template("""

  You have been invited to a Vinely Party by {{ invite_host_name }} ({{ invite_host_email }}).

    Party: "{{ party.title }}"
    {% if party.description %}{{ party.description }}{% endif %}
    Date: {{ party.event_date|date:"F j, o" }}
    Time: {{ party.event_date|date:"g:i A" }}

  You need RSVP to your party invitation at:

    http://{{ host_name }}{% url party_rsvp party.id %}

  Please do this as soon as possible.  

  Thank you!

  from your Vinely Specialists

  """)

  c = Context({"party": party_invite.party,
              "invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
              "invite_host_email": request.user.email,
              "host_name": request.get_host()})
  message = message_template.render(c)

  # send out verification e-mail, create a verification code
  subject = "You are invited to a Vinely Party!"
  send_mail(subject, message, 'support@vinely.com', [party_invite.invitee.email])

def distribute_party_invites_email(request, invitation_sent):

  message_template = Template("""

  You have been invited to a Vinely Party by {{ invite_host_name }} ({{ invite_host_email }}).

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

  from your Vinely Specialists

  """)

  c = Context({"party": invitation_sent.party,
              "custom_message": invitation_sent.custom_message,
              "invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name) if request.user.first_name else "Friendly Host",
              "invite_host_email": request.user.email,
              "host_name": request.get_host()})
  message = message_template.render(c)

  recipients = []
  for guest in invitation_sent.guests.all():
    recipients.append(guest.email)

  send_mail(invitation_sent.custom_subject, message, 'support@vinely.com', recipients)

