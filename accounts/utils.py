from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Context, Template
from django.template.loader import render_to_string

def send_verification_email(request, verification_code, temp_password, receiver_email):

  message_template = Template("""

  Please verify your e-mail address and create a new password by going to:

  http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.

  from your Vinely specialists.

  """)

  c = Context({"host_name": request.get_host(),
              "verification_code": verification_code,
              "temp_password": temp_password})
  message = message_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Welcome to Vinely!'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  msg = EmailMultiAlternatives(subject, message, 'support@vinely.com', recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_password_change_email(request, verification_code, temp_password, receiver_email):

  message_template = Template("""

  You have requested for your password to be reset, please use the temporary password 
  and update your account with a new password at:

  http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.

  from your Vinely specialists.

  """)

  c = Context({"host_name": request.get_host(),
              "verification_code": verification_code,
              "temp_password": temp_password})
  message = message_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Change password request'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  msg = EmailMultiAlternatives(subject, message, 'support@vinely.com', recipients)
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

  from your Vinely specialists.

  """)

  c = Context({"party_name": party_invite.party.title, 
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
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  msg = EmailMultiAlternatives(subject, message, 'support@vinely.com', recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_party_email(request, verification_code, temp_password, receiver_email):

  message_template = Template("""

  You have been approved to host a new Vinely party by {{ invite_host_name }} ({{ invite_host_email }}).

  Please verify your e-mail address and create a new password by going to:

  http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.


  from your Vinely Specialists

  """)

  c = Context({"invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
              "invite_host_email": request.user.email,
              "host_name": request.get_host(),
              "verification_code": verification_code,
              "temp_password": temp_password})
  message = message_template.render(c)

  # send out email approving host 
  subject = 'Welcome to Vinely!'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", {'title': subject, 'message': message})

  msg = EmailMultiAlternatives(subject, message, 'support@vinely.com', recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

