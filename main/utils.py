from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import RequestContext,   Context, Template
from django.template.loader import render_to_string
from django.contrib.auth.models import Group

from main.models import Order, EngagementInterest, MyHost, PartyInvite
from support.models import Email

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
  content = """
    Hey {{ customer }},


    Thank you for choosing Vinely!

    Your order {{ order_id }} has been received and you should expect your delicious surprise in 7 - 10 business days. Remember, someone 21 years or older must be available to receive your order.

    Keep an eye on your inbox over the next few days, as we will be sending further shipping information.  You can check the status of your order at:

      http://{{ host_name }}{% url order_complete order_id %}

    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,
  
    - The Vinely Team

  """

  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  subject = 'Your Vinely order was placed successfully!'
  from_email = 'Vinely Sales <sales@vinely.com>'

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

  Dear Supplier,

  Customer ({{ customer }}) has completed an order. Please process the order as soon as possible.  You can check the status of their order at:

    http://{{ host_name }}{% url supplier_edit_order order_id %}

  {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

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

  from_email = 'Vinely Parties <welcome@vinely.com>'
  recipients = ['sales@vinely.com']

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # notify the supplier that an order has been received
  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  order.fulfill_status = 1
  order.save()

def send_order_shipped_email(request, order):
  content = """

  Dear {% if order.receiver.first_name %}{{ order.receiver.first_name }}{% else %}Valued Customer{% endif %},

  Your order has been shipped and you should receive your order in the next 7 days.  You can check the status of your order at:

    http://{{ host_name }}{% url order_complete order.order_id %}

  {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

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
  from_email = 'Vinely Sales <sales@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_host_vinely_party_email(request, user, pro=None):
  # needs user param for when not logged in e.g. brand new host signing up
  content = """

  Hey {{ pro_first_name }}!

  Guess what? (Drumroll, please.) Someone in your area would like to be a host at a Vinely Taste Party! Please follow up ASAP to help set up an event date, make recommendations, and answer any possible questions.

  Name: {{ first_name }} {{ last_name }}

  Email Address: {{ email }} 

  {% if phone %}
  Phone: {{ phone }}
  {% endif %}

  Zipcode: {{ zipcode }}

  If you have any questions, please contact a Vinely Care Specialist at (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 

  {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team
 
  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))
  
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
  from_email = user.email

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

def send_know_pro_party_email(request, user, mentor_pro):

  content = """

  Hey {{ host_first_name }}!

  We're thrilled about your interest in hosting a Vinely Taste Party!  Since you already have a Vinely Pro in mind, they will soon be in contact to set a date and time.  If you haven't heard anything in 48 hours, please contact a Vinely Care Specialist at:

    (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 

  {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  c = RequestContext( request, {"host_first_name": user.first_name if user.first_name else "Vinely Host"})

  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)

  subject = 'Get the party started with Vinely'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = "Vinely Sales <sales@vinely.com>"
  recipients = [mentor_pro.email]
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_not_in_area_party_email(request):

  content = """

  Hey {{ host_first_name }}!

  We have some good news and some bad news.

  The Bad News: Vinely does not currently operate in your area. (Bummer, right?)

  The Good News: Your interest in Vinely is super important to us! So much, in fact, 
  that when we do expand to your area, you'll be the very first to know.

  If you have any questions, please contact a Vinely Care Specialist at: 

    (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 

  {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  c = RequestContext( request, {"host_first_name": request.user.first_name if request.user.first_name else "Vinely Host"})

  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)

  subject = 'Thanks for your interest in becoming a Vinely Host!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = request.user.email

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_party_scheduled_email(request, party):

  """

  Dear {{ host_first_name }},

  The following party has been scheduled:

    Party: "{{ party.title }}"
    {% if party.description %}{{ party.description }}{% endif %}
    Date: {{ party.event_date|date:"F j, o" }}
    Time: {{ party.event_date|date:"g:i A" }}


  You can start inviting guests to your party at:

    http://{{ host_name }}{% url party_taster_invite party.id %}
  
  If you have any questions, please contact me via e-mail: {{ pro_email }} {% if pro_phone %}or via phone: {{ pro_phone }}{% endif %} 

  Look forward to seeing you soon!

  {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Vinely Pro {{ pro_first_name }} {{ pro_last_name }}

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x])) #Template("<pre>%s</pre>" % content)

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
  from_email = request.user.email

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_party_invitation_email(request, party_invite):
  """ 
    individual invitation e-mail
  """
  content = """

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

  {% if plain %}
  Click on this link to RSVP Now: http://{{ host_name }}{% url party_rsvp party.id %}
  {% else %}
  <div class="email-rsvp-button"><a href="http://{{ host_name }}{% url party_rsvp party.id %}">RSVP Now</a></div>
  {% endif %}

  {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  c = RequestContext( request, {"party": party_invite.party,
              "invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
              "invite_host_email": request.user.email,
              "host_name": request.get_host(), "plain":True})
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  # send out party invitation e-mail 
  subject = "%s has invited you to a Vinely Taste Party!" % party_invite.party.host.first_name if party_invite.party.host.first_name else "Your Favorite Host"

  recipients = [party_invite.invitee.email]  
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'header': 'Good wine and good times await', 
                                                            'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Parties <welcome@vinely.com>'
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def distribute_party_invites_email(request, invitation_sent):
  content = """

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

  {% if plain %}
  Click on this link to RSVP Now: http://{{ host_name }}{% url party_rsvp party.id %}
  {% else %}
  <div class="email-rsvp-button"><a href="http://{{ host_name }}{% url party_rsvp party.id %}">RSVP Now</a></div>
  {% endif %}

  {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team


  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  c = RequestContext( request, {"party": invitation_sent.party,
              "custom_message": invitation_sent.custom_message,
              "invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name) if request.user.first_name else "Friendly Host",
              "invite_host_email": request.user.email,
              "host_name": request.get_host(), "plain":True})
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
  from_email = 'Vinely Parties <welcome@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  return msg

def send_rsvp_thank_you_email(request):

  content = """

    Hey, {{ first_name }}!

    Guess what? (Drumroll, please.) Your RSVP was received successfully! Now you can prepare to be paired with a Vinely Personality.

    Please fill out our quick 11-question survey. It will give us a glimpse into your personal taste. No pressure here. There's no right or wrong answer.

    {% if plain %}
    Click on this link to fill out the questionnaire: http://{{ host_name }}{% url pre_questionnaire_general %}
    {% else %}
    <a class="brand-btn" ref="http://{{ host_name }}{% url pre_questionnaire_general %}">Take the First Step</a>
    {% endif %}

    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    - The Vinely Team

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  c = RequestContext( request, {"first_name": request.user.first_name} )
  txt_message = txt_template.render(c)
  c.update({'sig':True, 'plain':False})
  html_message = html_template.render(c)

  recipients = [ request.user.email ]

  # send out party invitation e-mail 
  subject = 'Thanks for the RSVP!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'header': 'Good wine and good times await', 
                                                            'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Parties <welcome@vinely.com>'

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
  content = """

  {% if contact_request.first_name %}{{ contact_request.first_name }} {{ contact_request.last_name }}{% else %}Potential Customer{% endif %}, is interested in Vinely.  Please reach out via

    E-mail: {{ contact_request.email }}
    Phone: {{ contact_request.phone }}

  Following message was submitted:

    Subject: {{ contact_request.subject }}

    {{ contact_request.message }}

    {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    - The Vinely Web Site
  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  c = RequestContext( request, {"contact_request": contact_request})
  txt_message = txt_template.render(c)
  html_message = html_template.render(c)

  # send e-mail to notify about contact request
  subject = "URGENT: Request for information"
  recipients = ['sales@vinely.com']
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = contact_request.email

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_pro_assigned_notification_email(request, pro, host):
  content = """

    Dear {% if host_user.first_name %}{{ host_user.first_name }} {{ host_user.last_name }}{% else %}Friendly Host{% endif %},

    A new Vinely Pro has been assigned to you and now you may request to host Vinely parties! Here's your Vinely Pro contact information:

    Name: {{ pro_user.first_name }} {{ pro_user.last_name }}
    E-mail: {{ pro_user.email }}
    Phone: {{ pro_user.get_profile.phone }} 

    Please reach out to your Pro and start your Vinely parties!

    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{{ STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    - The Vinely Team

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))

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

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
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
