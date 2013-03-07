from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import RequestContext, Context, Template
from django.template.loader import render_to_string
from django.contrib.auth.models import User, Group
from django.utils import timezone

from main.models import Order, EngagementInterest, MyHost, PartyInvite
from support.models import Email
from accounts.models import VinelyProAccount, VerificationQueue
from datetime import tzinfo, timedelta
from cms.models import Section

from premailer import Premailer

import uuid
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


def send_order_added_email(request, order_id, user_email, verification_code=None, temp_password=None):
  """
    The next method: send_to_supplier_order_added_email has to be called after this method is called
    to update order status to Ordered
  """
  order = Order.objects.get(order_id=order_id)
  user = User.objects.get(email=user_email)
  if order.fulfill_status > 0:
    # return if already processing since e-mail has already been sent
    return

  content = """
   {% load static %}

    Hey {{ customer }},

    Thank you for choosing Vinely!

    Your order {{ vinely_order_id }} has been received and your delicious surprise should arrive in 7 - 10 business days. Remember, someone 21 years or older must be available to receive your order.
    {% if verification_code %}
    If you are a new user, a new Vinely account has been created for you and you can verify using the following temporary password:

      Your temporary password is: {{ temp_password }}

    at:

      http://{{ host_name }}{% url verify_account verification_code %}
    {% endif %}

    Keep an eye on your inbox over the next few days, as we will be sending further shipping information.  You can check the status of your order at:

      http://{{ host_name }}{% url order_complete order_id %}

    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.processing"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

  """

  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  subject = 'Your Vinely order was placed successfully!'
  from_email = 'Vinely Order <info@vinely.com>'
  recipients = [user_email]

  c = RequestContext(request, {"customer": user.first_name if user.first_name else "Vinely Fan",
              "host_name": request.get_host(),
              "vinley_order_id": order.vinely_order_id,
              "order_id": order_id,
              "verification_code": verification_code,
              "temp_password": temp_password,
              "title": subject})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request,
      {'title': subject, 'message': html_message, 'host_name': request.get_host()}
    ))

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # notify the receiver that the order has been received
  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'order@vinely.com'})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_to_supplier_order_added_email(request, order_id):

  order = Order.objects.get(order_id=order_id)

  if order.fulfill_status > 0:
    # return if already processing since e-mail has already been sent
    return

  # formulate e-mail to the supplier
  content = """
  {% load static %}
  Dear Supplier,

  Customer ({{ customer }} from {{ state }}) has completed an order. Please process the order as soon as possible.  You can check the details of their order at:

    http://{{ host_name }}{% url supplier_edit_order order_id %}

  {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team

  """

  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))
  subject = 'Order ID: %s has been submitted!' % order.vinely_order_id

  c = RequestContext(request, {"customer": order.receiver.first_name if order.receiver.first_name else "Vinely Fan",
              "state": order.shipping_address.state,
              "host_name": request.get_host(),
              "order_id": order_id,
              "title": subject})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request,
    {'title': subject, 'message': html_message, 'host_name': request.get_host()}))

  from_email = 'Vinely Order <info@vinely.com>'
  recipients = ['fulfillment@vinely.com']

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # notify the supplier that an order has been received
  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'order@vinely.com'})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  order.fulfill_status = 1
  order.save()


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
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  subject = 'Your Vinely order was placed successfully!'
  from_email = 'Vinely Order <info@vinely.com>'
  recipients = [order.receiver.email]

  c = RequestContext(request, {"customer": order.receiver.first_name if order.receiver.first_name else "Vinely Fan",
              "host_name": request.get_host(),
              "state": order.shipping_address.state,
              "vinely_order_id": order.vinely_order_id,
              "order_id": order_id,
              "title": subject})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request,
      {'title': subject, 'message': html_message, 'host_name': request.get_host()}
    ))

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # notify the receiver that the order has been received
  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'order@vinely.com'})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  # formulate e-mail to the supplier
  content = """
  {% load static %}
  Dear Supplier,

  Customer ({{ customer }} from {{ state }}) has completed an order. Please process the order as soon as possible.  You can check the details of their order at:

    http://{{ host_name }}{% url supplier_edit_order order_id %}

  {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team

  """

  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  subject = 'Order ID: %s has been submitted for %s!' % (order.vinely_order_id, order.shipping_address.state)
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request,
    {'title': subject, 'message': html_message, 'host_name': request.get_host()}))

  from_email = 'Vinely Order <info@vinely.com>'
  if "mi" in str(order.shipping_address.state).lower():
    recipients = ['pmfaba@gmail.com']
  else:
    recipients = ['fulfillment@vinely.com']

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # notify the supplier that an order has been received
  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'order@vinely.com'})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  order.fulfill_status = 1
  order.save()


def send_order_shipped_email(request, order):

  template = Section.objects.get(template__key='order_shipped_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext(request, {"order": order, "host_name": request.get_host()})
  txt_message = txt_template.render(c)

  c.update({'sig': True})
  html_message = html_template.render(c)

  receiver_email = order.receiver.email
  sender_email = order.ordered_by.email

  recipients = [receiver_email]
  if sender_email != receiver_email:
    recipients.append(sender_email)

  subject = 'Order ID: %s has been shipped!' % order.order_id
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request,
    {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Order <info@vinely.com>'

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients,
                              headers={'Reply-To': 'order@vinely.com'}, bcc=['fulfillment@vinely.com'])

  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_host_vinely_party_email(request, user, pro=None):

  template = Section.objects.get(template__key='host_vinely_party_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  profile = user.get_profile()

  c = RequestContext(request, {"first_name": user.first_name if user.first_name else "Vinely",
                                "last_name": user.last_name if user.last_name else "Fan",
                                "email": user.email,
                                "pro_first_name": pro.first_name if pro and pro.first_name else "Care Specialist",
                                "phone": profile.phone,
                                "host_name": request.get_host(),
                                "zipcode": user.get_profile().zipcode})

  txt_message = txt_template.render(c)

  c.update({'sig': True})
  html_message = html_template.render(c)

  # new engagement interest
  recipients = ['sales@vinely.com']
  if pro:
    recipients.append(pro.email)

  # notify interest in hosting to Vinely Pro or vinely sales
  subject = 'A Vinely Taste Party is ready to be scheduled'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = ('Vinely Party <info@vinely.com>')

  # update our DB that there was repeated interest
  interest, created = EngagementInterest.objects.get_or_create(user=user, engagement_type=EngagementInterest.ENGAGEMENT_CHOICES[6][0])
  if not created:
    interest.update_time()

  p = Premailer(html_msg)
  html_msg = p.transform()

  # send out e-mail regardless
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': user.email})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  # return text message for display
  return txt_message


def send_new_party_scheduled_email(request, party):

  template = Section.objects.get(template__key='new_party_scheduled_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  profile = request.user.get_profile()

  c = RequestContext(request, {"host_first_name": party.host.first_name if party.host.first_name else "Superb Host",
              "pro_email": request.user.email,
              "pro_phone": profile.phone,
              "pro_first_name": request.user.first_name,
              "pro_last_name": request.user.last_name,
              "party": party,
              "host_name": request.get_host()})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  # notify host about scheduled party
  recipients = [party.host.email]
  subject = 'Your Vinely Party has been Scheduled!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))

  p = Premailer(html_msg)
  html_msg = p.transform()

  from_email = ('Vinely Party <info@vinely.com>')

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients,
                                headers={'Reply-To': request.user.email}, bcc=['care@vinely.com'])
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  # notify pro and care
  content = """

  Dear {{ pro_first_name }},

  The following party has been scheduled:

  Party: "{{ party.title }}"

  Host: {{ party.host.first_name }} {{ party.host.last_name }} <{{ party.host.email }}>

  Date: {{ party.event_date|date:"F j, o" }}

  Time: {{ party.event_date|date:"g:i A" }}

  Location: {{ party.address.full_text }}

  {% if party.description %}Party Details: {{ party.description }}{% endif %}

  {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team

  """
  # template = Section.objects.get(template__key='new_party_scheduled_email', category=0)
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  profile = request.user.get_profile()

  c = RequestContext(request, {"pro_first_name": party.pro.first_name if party.pro.first_name else "Care Specialist",
              "party": party,
              "host_name": request.get_host()})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  # notify about scheduled party
  recipients = [party.pro.email, 'care@vinely.com']
  subject = 'Your Vinely Party has been Scheduled!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = ('Vinely Party <info@vinely.com>')

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': request.user.email})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_party_scheduled_by_host_no_pro_email(request, party):
  template = Section.objects.get(template__key='new_party_scheduled_by_host_no_pro_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext(request, {"party": party, "host_name": request.get_host()})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  # notify about scheduled party
  recipients = [party.host.email]
  subject = 'Your Vinely Party has been Submitted!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = ('Vinely Party <info@vinely.com>')

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'care@vinely.com'})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_party_scheduled_by_host_email(request, party):

  template = Section.objects.get(template__key='new_party_scheduled_by_host_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  if party.pro:
    c = RequestContext(request, {"pro": party.pro,
                                "invite_host_name": request.user.first_name if request.user.first_name else "Friendly Host",
                                "party": party,
                                "pro_name": "%s %s" % (party.pro.first_name, party.pro.last_name) if party.pro.first_name else "Care Specialist",
                                "pro_phone": party.pro.get_profile().phone,
                                "has_pro": party.pro,
                                "host_name": request.get_host()})
  else:
    c = RequestContext(request, {"pro": "No pro",
                                "invite_host_name": request.user.first_name if request.user.first_name else "Friendly Host",
                                "party": party,
                                "pro_name": "Care Specialist",
                                "pro_phone": "No phone number",
                                "has_pro": party.pro,
                                "host_name": request.get_host()})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  # notify about scheduled party
  recipients = [party.host.email]
  subject = 'Your Vinely Party has been Scheduled!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = ('Vinely Party <info@vinely.com>')

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'care@vinely.com'})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def distribute_party_invites_email(request, invitation_sent):

  content = invitation_sent.custom_message if invitation_sent.custom_message else get_default_invite_message(invitation_sent.party)
  # html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  host_user = invitation_sent.party.host
  inviting_user = request.user

  subject = invitation_sent.custom_subject

  party_info = get_party_info(invitation_sent.party)
  content += "\n\n" + party_info

  signature = invitation_sent.signature if invitation_sent.signature else get_default_signature(invitation_sent.party)
  content += "\n\n" + signature

  from_email = 'Vinely Party Invite <info@vinely.com>'
  if inviting_user.first_name:
    from_email = 'Invitation from %s %s <info@vinely.com>' % (inviting_user.first_name, inviting_user.last_name)
  else:
    from_email = 'Invitation from %s %s <info@vinely.com>' % (host_user.first_name, host_user.last_name)
  guests = invitation_sent.guests.exclude(id=host_user.id)
  for guest in guests:
    invite = PartyInvite.objects.get(invitee=guest, party=invitation_sent.party)
    invite.invited_timestamp = timezone.now()
    invite.save()

    if not guest.is_active:
      # new user created through party invitation
      temp_password = User.objects.make_random_password()
      guest.set_password(temp_password)
      guest.save()

      if VerificationQueue.objects.filter(user=guest, verified=False).exists():
        vque = VerificationQueue.objects.filter(user=guest, verified=False).order_by('-created')[0]
        verification_code = vque.verification_code
      else:
        verification_code = str(uuid.uuid4())
        vque = VerificationQueue(user=guest, verification_code=verification_code)
        vque.save()

    c = RequestContext(request, {'host_name': request.get_host(), 'invite': invite})
    user_content = content + '\n\n<a class="brand-btn" href="http://{{ host_name }}{% url party_rsvp invite.rsvp_code invite.party.id  %}">RSVP for the Party</a> \n'

    html_template = Template('\n'.join(['<p>%s</p>' % x for x in user_content.split('\n\n') if x]))
    html_message = html_template.render(c)
    txt_message = user_content

    # send out party invitation e-mail
    html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                              'header': 'Good wine and good times await',
                                                              'message': html_message, 'host_name': request.get_host()}))
    recipients = [guest.email]

    p = Premailer(html_msg)
    html_msg = p.transform()

    email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
    email_log.save()

    msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'welcome@vinely.com'})
    msg.attach_alternative(html_msg, "text/html")
    msg.send()

  # return msg
  return guests.count()


def preview_party_invites_email(request, invitation_sent, embed=False):

  content = invitation_sent.custom_message if invitation_sent.custom_message else get_default_invite_message(invitation_sent.party)

  subject = invitation_sent.custom_subject

  party_info = get_party_info(invitation_sent.party)
  content += "\n\n" + party_info

  signature = invitation_sent.signature if invitation_sent.signature else get_default_signature(invitation_sent.party)
  content += "\n\n" + signature

  c = RequestContext(request, {'host_name': request.get_host(),
                                'sig': True})

  content += '\n\n<a class="brand-btn" href="#">RSVP for the Party</a> \n'

  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))
  html_message = html_template.render(c)

  # send out party invitation e-mail
  if embed:
    html_msg = render_to_string("email/base_email_embed.html", RequestContext(request, {'title': subject,
                                                            'header': 'Good wine and good times await',
                                                            'message': html_message, 'host_name': request.get_host()}))
  else:
    html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                            'header': 'Good wine and good times await',
                                                            'message': html_message, 'host_name': request.get_host()}))
  return html_msg


def preview_party_thanks_note_email(request, thanks_note, embed=False):
  template = Section.objects.get(template__key='distribute_party_thanks_note_email', category=0)
  content = thanks_note.custom_message if thanks_note.custom_message else template.content

  subject = thanks_note.custom_subject

  c = RequestContext(request, {'party': thanks_note.party,
                              'host_name': request.get_host(),
                              "pro_email": thanks_note.party.pro.email,
                              'show_text_sig': True, 'sig': True})

  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))
  html_message = html_template.render(c)

  # send out party thanks e-mail
  if embed:
    html_msg = render_to_string("email/base_email_embed.html", RequestContext(request, {'title': subject,
                                                            'header': 'Thanks for being part of the amazing Vinely experience',
                                                            'message': html_message, 'host_name': request.get_host()}))
  else:
    html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                            'header': 'Thanks for being part of the amazing Vinely experience',
                                                            'message': html_message, 'host_name': request.get_host()}))
  return html_msg


def resend_party_invite_email(request, user, invitation_sent):

  content = invitation_sent.custom_message if invitation_sent.custom_message else get_default_invite_message(invitation_sent.party)

  # html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  host_user = invitation_sent.party.host
  inviting_user = host_user

  subject = invitation_sent.custom_subject

  from_email = 'Vinely Party Invite <info@vinely.com>'
  if inviting_user.first_name:
    from_email = 'Invitation from %s %s <info@vinely.com>' % (inviting_user.first_name, inviting_user.last_name)
  else:
    from_email = 'Invitation from %s %s <info@vinely.com>' % (host_user.first_name, host_user.last_name)

  for guest in invitation_sent.guests.filter(id=user.id):
    invite = PartyInvite.objects.get(invitee=guest, party=invitation_sent.party)

    c = RequestContext(request, {'host_name': request.get_host(), 'invite': invite})

    content += '\n\n<a class="brand-btn" href="http://{{ host_name }}{% url party_rsvp invite.rsvp_code invite.party.id  %}">RSVP for the Party</a> \n'

    html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))
    html_message = html_template.render(c)
    txt_message = content

    # send out party invitation e-mail
    html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                              'header': 'Good wine and good times await',
                                                              'message': html_message, 'host_name': request.get_host()}))
    recipients = [guest.email]

    p = Premailer(html_msg)
    html_msg = p.transform()

    email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
    email_log.save()

    msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'welcome@vinely.com'})
    msg.attach_alternative(html_msg, "text/html")
    msg.send()

  # return msg


def send_rsvp_thank_you_email(request, user, verification_code, temp_password):

  template = Section.objects.get(template__key='rsvp_thank_you_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext(request, {"first_name": user.first_name,
                                "host_name": request.get_host()})

  if verification_code:
    c.update({'verification_code': verification_code, 'temp_password': temp_password})

  txt_message = txt_template.render(c)
  c.update({'sig': True, 'plain': False})
  html_message = html_template.render(c)

  recipients = [user.email]

  # send out party invitation e-mail
  subject = 'Thanks for the RSVP!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                            'header': 'Good wine and good times await',
                                                            'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Confirmation <info@vinely.com>'

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'welcome@vinely.com'})
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

  c = RequestContext(request, {"contact_request": contact_request})
  txt_message = txt_template.render(c)
  html_message = html_template.render(c)

  # send e-mail to notify about contact request
  subject = "URGENT: Request for information"
  recipients = ['sales@vinely.com']
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message,
                                                                                    'host_name': request.get_host()}))
  from_email = ('Vinely <info@vinely.com>')

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': contact_request.email})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_pro_assigned_notification_email(request, pro, host):

  template = Section.objects.get(template__key='pro_assigned_notification_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext(request, {"host_user": host, "pro_user": pro})
  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  # send e-mail to notify about contact request
  subject = "Congratulations! Vinely Pro has been assigned to you."
  recipients = [host.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                                                      'message': html_message,
                                                                                      'host_name': request.get_host()}))
  from_email = "Vinely Update <info@vinely.com>"

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients,
                              headers={'Reply-To': 'care@vinely.com'}, bcc=['care@vinely.com'])

  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_mentor_assigned_notification_email(request, mentee, mentor):

  template = Section.objects.get(template__key='mentor_assigned_notification_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext(request, {"mentee": mentee, "mentor": mentor})
  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  # send e-mail to notify about contact request
  subject = "Congratulations! Vinely Mentor has been assigned to you."
  recipients = [mentee.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = "Vinely Update <info@vinely.com>"

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients,
                              headers={'Reply-To': 'care@vinely.com'}, bcc=['care@vinely.com'])

  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_mentee_assigned_notification_email(request, mentor, mentee):

  template = Section.objects.get(template__key='mentee_assigned_notification_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext(request, {"mentor": mentor, "mentee": mentee})
  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  # send e-mail to notify about contact request
  subject = "Congratulations! Vinely Mentee has been assigned to you."
  recipients = [mentor.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = "Vinely Update <info@vinely.com>"

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients,
                              headers={'Reply-To': 'care@vinely.com'}, bcc=['care@vinely.com'])
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_welcome_to_vinely_email(request, taster, verification_code, temp_password):
  template = Section.objects.get(template__key='welcome_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext(request, {
              "taster_first_name": taster.first_name,
              "verification_code": verification_code,
              "temp_password": temp_password,
              "host_name": request.get_host(),
              "plain": True})

  txt_message = txt_template.render(c)
  c.update({'sig': True, 'plain': False})
  html_message = html_template.render(c)

  # send out party invitation e-mail
  subject = 'Welcome to Vinely'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                            'header': 'Welcome to Vinely',
                                                            'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Welcome to Vinely <welcome@vinely.com>'
  recipients = [taster.email]
  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'welcome@vinely.com'})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def distribute_party_thanks_note_email(request, note_sent, guest_invites, placed_order):
  template = Section.objects.get(template__key='distribute_party_thanks_note_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  # recipients = []
  for invite in guest_invites:
    recipients = [invite.invitee.email]
    c = RequestContext(request, {"party": note_sent.party,
                "taster_first_name": invite.invitee.first_name,
                "pro_email": invite.party.pro.email,
                "custom_message": note_sent.custom_message,
                "party_host_name": "%s %s" % (request.user.first_name, request.user.last_name) if request.user.first_name else "Friendly Host",
                "party_host_email": request.user.email,
                "host_name": request.get_host(), "placed_order": placed_order,
                "plain": True, 'show_text_sig': True})

    txt_message = txt_template.render(c)
    c.update({'sig': True, 'plain': False})
    html_message = html_template.render(c)

    # send out party invitation e-mail
    subject = note_sent.custom_subject
    html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                              'header': 'Thanks for being part of the amazing Vinely experience',
                                                              'message': html_message, 'host_name': request.get_host()}))
    from_email = 'Thank You <info@vinely.com>'

    p = Premailer(html_msg)
    html_msg = p.transform()

    email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
    email_log.save()

    msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': 'welcome@vinely.com'})
    msg.attach_alternative(html_msg, "text/html")
    msg.send()

  # return msg


def send_host_request_party_email(request, party):
  template = Section.objects.get(template__key='host_request_party_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  host_first_name = request.user.first_name if request.user.first_name else "Vinely"
  host_last_name = request.user.last_name if request.user.last_name else "Host"

  c = RequestContext(request, {"party": party,
              "invite_host_name": "%s %s" % (host_first_name, host_last_name) if request.user.first_name else "Friendly Host",
              # "host_email": request.user.email,
              "host_phone": request.user.userprofile.phone,
              "pro_name": "%s %s" % (party.pro.first_name, party.pro.last_name) if party.pro and party.pro.first_name else "Care Specialist",
              "host_name": request.get_host(), "plain": True})
  txt_message = txt_template.render(c)
  c.update({'sig': True, 'plain': False})
  html_message = html_template.render(c)

  # send out party invitation e-mail

  subject = "%s %s would like to host a party" % (host_first_name, host_last_name)
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                            'header': 'Let\'s get the party started',
                                                            'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Party Request <info@vinely.com>'

  if party.pro:
    recipients = [party.pro.email]
    bcc = ['care@vinely.com']
  else:
    recipients = ['care@vinely.com']
    bcc = []

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients,
                              headers={'Reply-To': request.user.email},  bcc=bcc)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  return msg


def send_new_party_host_confirm_email(request, party):
  template = Section.objects.get(template__key='new_party_host_confirm_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  host_first_name = party.host.first_name if party.host.first_name else "Friendly Host"

  c = RequestContext(request, {"party": party,
              "invite_host_name": "%s" % host_first_name,
              "pro": party.pro,
              "pro_phone": party.pro.userprofile.phone,
              "pro_name": "%s" % party.pro.first_name if party.pro and party.pro.first_name else "Care Specialist",
              "host_name": request.get_host(), "plain": True})
  txt_message = txt_template.render(c)
  c.update({'sig': True, 'plain': False})
  html_message = html_template.render(c)

  # send out party invitation e-mail

  subject = "Your Vinely Taste Party has been scheduled!"
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject,
                                                            'header': 'Let\'s get the party started',
                                                            'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Party Confirmation <sales@vinely.com>'

  recipients = [party.host.email]

  p = Premailer(html_msg)
  html_msg = p.transform()

  host_email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  host_email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients,
                              headers={'Reply-To': request.user.email})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  # notify pro and care
  content = """

  Dear {{ pro_first_name }},

  The following party has been scheduled:

  Party: "{{ party.title }}"

  Host: {{ party.host.first_name }} {{ party.host.last_name }} <{{ party.host.email }}>

  Date: {{ party.event_date|date:"F j, o" }}

  Time: {{ party.event_date|date:"g:i A" }}

  Location: {{ party.address.full_text }}

  {% if party.description %}Party Details: {{ party.description }}{% endif %}

  {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team

  """
  # template = Section.objects.get(template__key='new_party_scheduled_email', category=0)
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))

  profile = request.user.get_profile()

  c = RequestContext(request, {"pro_first_name": party.pro.first_name if party.pro.first_name else "Care Specialist",
              "party": party,
              "host_name": request.get_host()})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  # notify about scheduled party
  recipients = [party.pro.email, 'care@vinely.com']
  subject = 'Your Vinely Party has been Scheduled!'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = ('Vinely Party <info@vinely.com>')

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': request.user.email})
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

  return host_email_log


def preview_host_confirm_email(request, party):
  template = Section.objects.get(template__key='new_party_host_confirm_email', category=0)
  # txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  host_first_name = party.host.first_name if party.host.first_name else "Friendly Host"

  pro, pro_profile = my_pro(request.user)
  party.id = 0
  c = RequestContext(request,  {"party": party,
                                "invite_host_name": "%s" % host_first_name,
                                "pro": pro,
                                "pro_phone": pro.userprofile.phone,
                                "pro_name": "%s" % pro.first_name if pro and pro.first_name else "Care Specialist",
                                "host_name": request.get_host(), "plain": True})
  # txt_message = txt_template.render(c)
  c.update({'sig': True, 'plain': False})
  html_message = html_template.render(c)

  # send out party invitation e-mail

  subject = "Your Vinely Taste Party has been scheduled!"
  html_msg = render_to_string("email/base_email_lite.html",
                              RequestContext(request,  {'title': subject,
                                                        'header': 'Let\'s get the party started',
                                                        'message': html_message, 'host_name': request.get_host()}))

  return html_msg


def party_setup_completed_email(request, party):
  template = Section.objects.get(template__key='party_setup_completed_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext(request,  {"pro_first_name": party.pro.first_name if party.pro.first_name else "Care Specialist",
                                "party": party,
                                "host_phone": party.host.userprofile.phone,
                                "host_name": request.get_host()})

  txt_message = txt_template.render(c)
  c.update({'sig': True})
  html_message = html_template.render(c)

  # notify about scheduled party
  recipients = [party.pro.email, 'care@vinely.com']
  subject = '%s has completed setting up their party!' % party.host.first_name
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = ('Vinely Party <info@vinely.com>')

  p = Premailer(html_msg)
  html_msg = p.transform()

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, headers={'Reply-To': request.user.email})
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

  # first host that invited me
  invitation = PartyInvite.objects.filter(invitee=user).order_by('invited_timestamp')
  if invitation.exists():
    return invitation[0].party.host

  return None


def my_pro(user):
  pro = user.userprofile.mentor
  pro_profile = user.userprofile.mentor.get_profile() if user.userprofile.mentor else None
  return pro, pro_profile

from django.db.models import Sum
from main.models import *
from datetime import timedelta, datetime


def calculate_host_credit(host):
  # get all past parties hosted by host
  today = datetime.now(tz=UTC())
  host_parties = Party.objects.filter(host=host, event_date__lt=today)

  # only calculate credit if they have hosted a party
  if not host_parties.exists():
    return 0

  available_credit = 0
  for party in host_parties:
    available_credit += party.credit()

  # total_orders = 0
  # for party in host_parties:
  #   # get orders made <= 7 days after party
  #   party_window = party.event_date + timedelta(days=7)

  #   orders = Order.objects.filter(cart__party=party, order_date__lte=party_window)
  #   # exclude orders made by host
  #   orders = orders.exclude(ordered_by=host)
  #   # should not be tasting kit
  #   orders = orders.exclude(cart__items__product__category=Product.PRODUCT_TYPE[0][0])
  #   aggregate = orders.aggregate(total=Sum('cart__items__total_price'))
  #   total_orders += aggregate['total'] if aggregate['total'] else 0

  # # sales < 399 = 0 credit
  # # 400 - 599 = 40
  # # 600 - 799 = 60
  # # 800 - 999 = 90
  # # 1000-1199 = 120
  # # 1200-1399 = 150
  # available_credit = 20 * host_parties.count()

  # total = int(total_orders + 1)
  # for cost in range(400, total, 200):
  #   if cost == 400:
  #     available_credit += 40
  #   elif cost > 800:
  #     available_credit += 30
  #   else:
  #     available_credit += 20

  # deduct used credit
  orders = Order.objects.filter(cart__receiver=host, cart__discount__gt=0)
  credit_aggregate = orders.aggregate(total=Sum('cart__discount'))
  credit_used = credit_aggregate['total'] if credit_aggregate['total'] else 0
  applicable_credit = available_credit - credit_used
  return applicable_credit if applicable_credit > 0 else 0

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
  org_parties = OrganizedParty.objects.filter(pro=pro)
  parties = [p.party for p in org_parties]
  basic_total = other_total = freq_total = mentee_total = 0
  for party in parties:
    orders = Order.objects.filter(cart__party=party)
    # exclude taste kits
    orders = orders.exclude(cart__items__product__category=Product.PRODUCT_TYPE[0][0])

    # get one-time basic orders
    one_time_basic = orders.filter(cart__items__frequency=SubscriptionInfo.FREQUENCY_CHOICES[0][0], cart__items__price_category__in=[5, 6])
    # get one-time divine, superior
    one_time_other = orders.filter(cart__items__frequency=SubscriptionInfo.FREQUENCY_CHOICES[0][0], cart__items__price_category__in=[7, 8, 9, 10])
    # get frequency buys
    freq_orders = orders.filter(cart__items__frequency__in=[1, 2, 3])

    basic_aggr = one_time_basic.aggregate(total=Sum('cart__items__total_price'))
    basic_total += basic_aggr['total'] if basic_aggr['total'] else 0

    other_aggr = one_time_other.aggregate(total=Sum('cart__items__total_price'))
    other_total += other_aggr['total'] if other_aggr['total'] else 0

    freq_aggr = freq_orders.aggregate(total=Sum('cart__items__total_price'))
    freq_total += freq_aggr['total'] if freq_aggr['total'] else 0

  # 2. calculate for mentee's parties
  # 5% of mentee's retail sales if within 120 days of party
  mentees = User.objects.filter(userprofile__mentor=pro)
  org_parties = OrganizedParty.objects.filter(pro__in=mentees)
  parties = [p.party for p in org_parties]

  for party in parties:
    # get orders made within 120 days after party
    party_window = party.event_date + timedelta(days=90)
    orders = Order.objects.filter(order_date__lte=party_window, cart__party=party)
    # exclude taste kits
    orders = orders.exclude(cart__items__product__category=Product.PRODUCT_TYPE[0][0])
    aggr = orders.aggregate(total=Sum('cart__items__total_price'))
    mentee_total += aggr['total'] if aggr['total'] else 0

  # returns tuple (<pro_commission from own parties>, <commission from mentee parties>)
  return ((0.1 * float(basic_total)) + (0.1 * float(other_total)) + (0.1 * float(freq_total)),  # pro commissions
           (0.05 * float(mentee_total))  # mentee commissions
          )

import re


def generate_pro_account_number():
  '''
  Generate a new account number for a pro in the format VP#####A
  '''
  #TODO: avoid race condition
  max = 99999
  accounts_to_ignore = ['VP00090A', 'VP00091A', 'VP00092A', 'VP00093A', 'VP00094A', 'VP00095A', 'VP00096A', 'VP00097A', 'VP00098A', 'VP00099A']
  latest = VinelyProAccount.objects.exclude(account_number__in=accounts_to_ignore).order_by('-account_number')[:1]
  if latest.exists():
    prefix = 'VP'  # latest[:2]
    account = latest[0].account_number
    suffix = account[7:]  # last chars(s) after number
    num = int(re.findall('\d+', account)[0])
    if num == max:
      last = suffix[-1]
      if last == 'Z':
        suffix += 'A'
        num = 1
      else:
        num = 1
        suffix = suffix[:-1] + chr(ord(last) + 1)
    else:
      num += 1
    acc_num = '%s%s%s' % (prefix, '%0*d' % (5, num), suffix)
  else:
    acc_num = 'VP00100A'
  return acc_num


def get_default_invite_message(party):
  message_text = '''

  Please join me for a Vinely Taste Party. Vinely is part wine tasting, part wine club, and part, well... party.

  We won't be...
  <ul>
    <li>Sniffing, swirling, spitting</li>
    <li>Using words like 'silky blackberry woodchips', 'wet dog', or 'notes of grass'</li>
    <li>Studying wine regions of the world</li>
  </ul>

  We will be...
  <ul>
    <li>Blind tasting 6 wines. Don't worry only the wine is blindfolded</li>
    <li>Using our tastebuds to rate those wines, no degree required</li>
    <li>Discovering our wine personalities. We'll separate the Moxies from the Sensational, the Exuberant from the Easygoing, and the Whimsical from the Serendipitous</li>
    <li>Ordering wines (well, at least those of us that want wine delivered that's hand selected just for our tastes!)</li>
  </ul>

  With Vinely, the more you drink, the more we learn about what you like. So let's start drinking our way to a future of wines we love at my place. I promise it will be nothing short of a good time.

  '''
  template = Template(message_text)
  context = Context()
  return template.render(context)


def get_party_info(party):
  info = """

  Party: {{ party.title }}

  Host: {{ party.host.first_name }} {{ party.host.last_name }} <{{ party.host.email }}>

  Date: {{ party.event_date|date:"F j, o" }}

  Time: {{ party.event_date|date:"g:i A" }}

  Location: {{ party.address.full_text }}
  """
  template = Template(info)
  context = Context({'party': party})
  return template.render(context)


def get_default_signature(party):
  sig_text = """

  Will you attend? You know you want to! RSVP by {{ rsvp_date|date:"F j, o" }}. Better yet, don't wait!

  {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team
  """
  template = Template(sig_text)
  rsvp_date = party.event_date - timedelta(days=5)
  context = Context({'rsvp_date': rsvp_date})
  return template.render(context)


def add_form_validation(form):
  from django import forms

  for field_name in form.fields:
    if form.fields[field_name].required:
      attrs = form.fields[field_name].widget.attrs
      attrs['class'] = attrs.get('class', '')
      if isinstance(form.fields[field_name], forms.EmailField):
        attrs['class'] += " validate[required,custom[email]"
      elif isinstance(form.fields[field_name], forms.DateField):
        attrs['class'] += " datepicker validate[required]"  # ,custom[date]"
      elif isinstance(form.fields[field_name], forms.TimeField):
        attrs['class'] += " timepicker validate[required]"
      elif isinstance(form.fields[field_name], forms.IntegerField):
        attrs['class'] += " validate[required,custom[number]"
      else:
        attrs['class'] += " validate[required]"

      if attrs['class']:
        form.fields[field_name].widget.attrs['class'] = attrs['class']
