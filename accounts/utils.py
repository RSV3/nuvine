from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import RequestContext, Context, Template
from django.template.loader import render_to_string

from support.models import Email

def send_verification_email(request, verification_code, temp_password, receiver_email):

  message_template = Template("""

  Please verify your e-mail address and create a new password by going to:

  http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.

  from your Vinely Pros.

  """)

  c = RequestContext( request, {"host_name": request.get_host(),
              "verification_code": verification_code,
              "temp_password": temp_password})
  message = message_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Welcome to Vinely!'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))
  from_email = 'support@vinely.com'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_password_change_email(request, verification_code, temp_password, user):

  message_template = Template("""

  Hey {% if first_name %}{{ first_name }}{% else %}{{ role.name }}{% endif %}!

  We heard you lost your password. (No prob.  Happens all the time.)

  Here's your temporary password: {{ temp_password }} 

  Please update your account with a new password at:

    http://{{ host_name }}{% url verify_account verification_code %}

  Use this password to verify your account and change your password.

  If you don't know why you're receiving this email, click <a href="">here</a>.

  <div class="signature">
    <img src="{{ STATIC_URL }}img/vinely_logo_signature.png">
  </div>
  Your Tasteful Friends,

  - The Vinely Team 

  """)

  receiver_email = user.email

  c = RequestContext( request, {
              "first_name": user.first_name,
              "role": user.groups.all()[0],
              "host_name": request.get_host(),
              "verification_code": verification_code,
              "temp_password": temp_password})
  message = message_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Your new password, courtesy of Vinely'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))
  from_email = 'support@vinely.com'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_invitation_email(request, verification_code, temp_password, party_invite):

  message_template = Template("""

  You have been invited to a Vinely Party [{{ party_name }}] by {{ invite_host_name }} ({{ invite_host_email }}).
  We have automatically created a new account for you.

  Please verify your e-mail address and create a new password by going to:

    http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.


  You need to also RSVP to your party invitation at:

    http://{{ host_name }}{% url party_rsvp party_id %}

  from your Vinely Pros.

  """)

  c = RequestContext( request, {"party_name": party_invite.party.title, 
              "party_id": party_invite.party.id,
              "invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
              "invite_host_email": request.user.email,
              "host_name": request.get_host(),
              "verification_code": verification_code,
              "temp_password": temp_password})
  message = message_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Join Vinely Party!'
  recipients = [party_invite.invitee.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))
  from_email = 'support@vinely.com'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_party_email(request, verification_code, temp_password, receiver_email):

  message_template = Template("""

  You have been approved to host a new Vinely party by {{ invite_host_name }} ({{ invite_host_email }}).

  Please verify your e-mail address and create a new password by going to:

  http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.


  from your Vinely Pros

  """)

  c = RequestContext( request, {"invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
              "invite_host_email": request.user.email,
              "host_name": request.get_host(),
              "verification_code": verification_code,
              "temp_password": temp_password})
  message = message_template.render(c)

  # send out email approving host 
  subject = 'Welcome to Vinely!'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': message}))
  from_email = 'support@vinely.com'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

