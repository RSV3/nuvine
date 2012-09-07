from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import RequestContext, Context, Template
from django.template.loader import render_to_string
from accounts.models import Zipcode, SUPPORTED_STATES

from support.models import Email

def send_verification_email(request, verification_code, temp_password, receiver_email):

  content = """

  {% load static %}

  Please verify your e-mail address and create a new password by going to:

  http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.
  
  {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

  from your Vinely Pros.

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))
  
  c = RequestContext( request, {"host_name": request.get_host(),
                                "verification_code": verification_code,
                                "temp_password": temp_password,
                                })
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Welcome to Vinely!'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Get Started <welcome@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_password_change_email(request, verification_code, temp_password, user):
  content = """

  {% load static %}

  Hey {% if first_name %}{{ first_name }}{% else %}{{ role.name }}{% endif %}!

  We heard you lost your password. (No prob.  Happens all the time.)

  Here's your temporary password: {{ temp_password }} 

  Please update your account with a new password at:

    http://{{ host_name }}{% url verify_account verification_code %}

  Use this password to verify your account and change your password.

  If you don't know why you're receiving this email, click <a href="mailto:care@vinely.com">here</a>.

  {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

  Your Tasteful Friends,

  - The Vinely Team 

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))
  
  receiver_email = user.email
  
  c = RequestContext( request, {"first_name": user.first_name,
                                "role": user.groups.all()[0],
                                "host_name": request.get_host(),
                                "verification_code": verification_code,
                                "temp_password": temp_password})
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  # send out verification e-mail, create a verification code
  subject = 'Your new password, courtesy of Vinely'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'support@vinely.com'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_invitation_email(request, verification_code, temp_password, party_invite):
  content = """

  {% load static %}

  You have been invited to a Vinely Party [{{ party_name }}] by {{ invite_host_name }} ({{ invite_host_email }}).
  We have automatically created a new account for you.

  Please verify your e-mail address and create a new password by going to:

    http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.


  You need to also RSVP to your party invitation at:

    http://{{ host_name }}{% url party_rsvp party_id %}

  {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}
  
  from your Vinely Pros.

  """

  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))
  
  c = RequestContext( request, {"party_name": party_invite.party.title, 
                                "party_id": party_invite.party.id,
                                "invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
                                "invite_host_email": request.user.email,
                                "host_name": request.get_host(),
                                "verification_code": verification_code,
                                "temp_password": temp_password})
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Join Vinely Party!'
  recipients = [party_invite.invitee.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'welcome@vinely.com'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_party_email(request, verification_code, temp_password, receiver_email):

  content = """

  {% load static %}

  You have been approved to host a new Vinely party by {{ invite_host_name }} ({{ invite_host_email }}).

  Please verify your e-mail address and create a new password by going to:

  http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.

  {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

  from your Vinely Pros

  """
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))
  
  c = RequestContext( request, {"invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
                                "invite_host_email": request.user.email,
                                "host_name": request.get_host(),
                                "verification_code": verification_code,
                                "temp_password": temp_password})
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  # send out email approving host 
  subject = 'Welcome to Vinely!'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'welcome@vinely.com'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_pro_request_email(request, receiver):

  content = """

  {% load static %}

  Hey, {{ first_name }}!

  We're thrilled about your interest in becoming a Vinely Pro.

  We will review your application soon and get back to you within the next 48hrs.

  If you haven't heard anything in 48 hours, please contact a Vinely Care Specialist at 
  (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us.

  {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}
  
  Your Tasteful Friends,

  - The Vinely Team 

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))

  c = RequestContext( request, {"first_name":receiver.first_name})
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  subject = 'Vinely Pro Request!'
  recipients = [receiver.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'welcome@vinely.com'
  
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()
  
  # send mail to vinely for pro approval
  send_pro_review_email(request, receiver)

def send_pro_review_email(request, user):
  '''
  Sent to sales@vinely.com to review and approve request to be a pro
  '''
  
  content = """

  Hey Care Specialist,

  Someone has sent a request to be a Vinely Pro!
  Please follow up ASAP to help set them up and answer any possible questions.

  Name: {{ first_name }} {{ last_name }}

  Email Address: {{ email }} 

  Zipcode: {{ zipcode }}

  {% if phone %}
  Phone: {{ phone }}
  {% endif %}

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))
  
  profile = user.get_profile()

  c = RequestContext( request, {"first_name": user.first_name if user.first_name else "Vinely", 
                                "last_name": user.last_name if user.last_name else "Fan",
                                "email": user.email,
                                "phone": profile.phone,
                                "zipcode":user.get_profile().zipcode})

  txt_message = txt_template.render(c)
  html_message = html_template.render(c)

  recipients = ['sales@vinely.com']

  # notify interest in hosting to Vinely Pro or vinely sales 
  subject = 'Vinely Pro Request'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'welcome@vinely.com'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # update our DB that there was repeated interest
  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_unknown_pro_email(request, user):

  content = """

  {% load static %}

    Hey, {{ first_name }}!

    We're thrilled about your interest in hosting a Vinely Taste Party!

    To ensure you'll be the host with the most, we'll need to pair you with a Vinely Pro. They'll be reaching out soon.

    If you haven't heard anything in 48 hours, please contact a Vinely Care Specialist at (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))

  c = RequestContext( request, {"first_name": user.first_name} )
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  # send out email request to sales@vinely.com 
  subject = 'Get the party started with Vinely'
  recipients = [user.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'welcome@vinely.com'
  
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_pro_approved_email(request, applicant):

  content = """

  {% load static %}

  Hey {{ applicant.first_name }},<br>

  Your application to become Vinely Pro has been approved.  You may now login to your account
  and start recruiting hosts for your taste parties!

  Go have some fun wine parties!

  {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}
  
  Your Tasteful Friends,

  - The Vinely Team 

  """
  
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))
  
  data = {"applicant": applicant}
  c = RequestContext( request, data)
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  # send out email request to sales@vinely.com 
  subject = 'Vinely Pro Approved!'
  recipients = ['sales@vinely.com', applicant.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'welcome@vinely.com'
  
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_not_in_area_party_email(request, user, account_type):
  content = """

  {% load static %}

    Hey, {{ first_name }}!

    We have some good news and some bad news.

    The Bad News: Vinely does not currently operate in your area. (Bummer, right?)

    The Good News: Your interest in Vinely is super important to us! So much, in fact, that when we do expand to your area, you'll be the very first to know.

    If you have any questions, please contact a Vinely Care Specialist at (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

  """
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n') if x]))

  c = RequestContext( request, {"first_name": user.first_name})
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  #print 'account ', account_type, type(account_type)
  subject = 'Thanks for your interest in becoming a Vinely %s!' % ('Pro' if account_type == 1  else 'Host')
  recipients = [user.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'welcome@vinely.com'
  
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def check_zipcode(request, user, account_type, zipcode=None):
  '''
  Check provided zipcode against existing ones to verify if vinely operates in the area
  '''
  try:
    if not zipcode:
      zipcode = user.get_profile().zipcode
    code = Zipcode.objects.get(code = zipcode, state__in = SUPPORTED_STATES)
    return True
  except Zipcode.DoesNotExist:
    # application for pro/host?
    send_not_in_area_party_email(request, user, account_type)
    return False
