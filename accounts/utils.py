from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import RequestContext, Context, Template
from django.template.loader import render_to_string
from djanog.contrib.auth.models import Group
from accounts.models import Zipcode, SUPPORTED_STATES

from support.models import Email
from cms.models import Section

def send_verification_email(request, verification_code, temp_password, receiver_email):

  template = Section.objects.get(template__key='verification_email', category=0)

  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"host_name": request.get_host(),
                                "verification_code": verification_code,
                                "temp_password": temp_password,
                                })
  txt_message = txt_template.render(c)

  c.update({'sig': True})
  html_message = html_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Welcome to Vinely!'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Welcome to Vinely <welcome@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_password_change_email(request, verification_code, temp_password, user):

  template = Section.objects.get(template__key='password_change_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  receiver_email = user.email

  vinely_taster_group = Group.objects.get(name="Vinely Taster")
  if user.groups.all().count() == 0:
    # the user is in a weird state without a role, so assign taster
    user.groups.add(vinely_taster_group)
    user.save()

  c = RequestContext(request, {"first_name": user.first_name,
                                "role": user.groups.all()[0],
                                "host_name": request.get_host(),
                                "verification_code": verification_code,
                                "temp_password": temp_password})
  txt_message = txt_template.render(c)

  c.update({'sig': True})
  html_message = html_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Your new password, courtesy of Vinely'
  recipients = [receiver_email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Support <support@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_invitation_email(request, verification_code, temp_password, party_invite):
  '''
  New account invitation - sent when host invites new taster
  '''

  template = Section.objects.get(template__key='new_invitation_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  inviter_full_name = "Your friend"
  if request.user.first_name:
    inviter_full_name = "%s %s" % (request.user.first_name, request.user.last_name)

  c = RequestContext(request, {"party_name": party_invite.party.title,
                                "party_id": party_invite.party.id,
                                "invite_host_name": inviter_full_name,
                                "invite_host_email": request.user.email,
                                "host_name": request.get_host(),
                                "verification_code": verification_code,
                                "temp_password": temp_password})
  txt_message = txt_template.render(c)

  c.update({'sig': True})
  html_message = html_template.render(c)

  # send out verification e-mail, create a verification code
  subject = '%s has invited you to a Vinely Party!' % inviter_full_name
  recipients = [party_invite.invitee.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext(request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Invitation from %s <welcome@vinely.com>' % inviter_full_name
  if inviter_full_name == "Your friend":
    from_email = 'Vinely Party Invite <welcome@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_new_party_email(request, verification_code, temp_password, receiver_email):
  '''
  Sent when Pro creates new Host for a party
  '''
  
  template = Section.objects.get(template__key='new_party_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))
  
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
  from_email = 'Get Started with Vinely <welcome@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_pro_request_email(request, receiver):
  '''
  Sent when user requests to be a Pro
  '''
  
  template = Section.objects.get(template__key='pro_request_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"first_name":receiver.first_name})
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  subject = 'Vinely Pro Request!'
  recipients = [receiver.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Get Started <welcome@vinely.com>'
  
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
  
  template = Section.objects.get(template__key='pro_review_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))
  
  profile = user.get_profile()

  c = RequestContext( request, {"first_name": user.first_name if user.first_name else "Vinely", 
                                "last_name": user.last_name if user.last_name else "Fan",
                                "email": user.email,
                                "phone": profile.phone,
                                "zipcode":user.get_profile().zipcode})

  txt_message = txt_template.render(c)
  html_message = html_template.render(c)

  recipients = ['sales@vinely.com', 'getstarted@vinely.com']

  # notify interest in hosting to Vinely Pro or vinely sales 
  subject = 'Vinely Pro Request'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'New Vinely Pro <getstarted@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  # update our DB that there was repeated interest
  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()


def send_know_pro_party_email(request, user):

  template = Section.objects.get(template__key='know_pro_party_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"host_first_name": user.first_name if user.first_name else "Vinely Host"})

  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)

  subject = 'Get the party started with Vinely'
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = "Welcome to Vinely <welcome@vinely.com>"
  recipients = [user.email]
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_unknown_pro_email(request, user):

  template = Section.objects.get(template__key='unknown_pro_party_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"first_name": user.first_name} )
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  # send out email request to sales@vinely.com 
  subject = 'Get the party started with Vinely'
  recipients = [user.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Welcome to Vinely <welcome@vinely.com>'
  
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_pro_approved_email(request, applicant):

  template = Section.objects.get(template__key='pro_approved_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))
  account_number = ''
  if applicant.vinelyproaccount_set.all().exists():
    account_number = applicant.vinelyproaccount_set.all()[0].account_number
  data = {"applicant": applicant, "pro_account_number": account_number}
  c = RequestContext( request, data)
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  # send out email request to sales@vinely.com 
  subject = 'Vinely Pro Approved!'
  recipients = [applicant.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely Update <care@vinely.com>'
  
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients, bcc=['sales@vinely.com'])
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_not_in_area_party_email(request, user, account_type):
  
  template = Section.objects.get(template__key='not_in_area_party_email', category=0)
  txt_template = Template(template.content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in template.content.split('\n\n') if x]))

  c = RequestContext( request, {"first_name": user.first_name})
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)
  
  if account_type == 1:
    user_group = 'Pro'
  elif account_type == 2:
    user_group = 'Host'
  elif account_type == 3:
    user_group = 'Taster'

  subject = 'Thanks for your interest in becoming a Vinely %s!' % user_group
  recipients = [user.email]
  html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  from_email = 'Vinely <welcome@vinely.com>'
  
  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()

def send_thank_valued_member_email(request, verification_code, temp_password, receiver_email):
  # need to get host_name when request = None
  content = """

  {% load static %}

  Dear Valued Vinely member,

  Thank you for being part of Vinely when we were a baby.  We now have online presence to serve your needs better.

  Your new account has been automatically created. Please verify your e-mail address and create a new password by going to:

  http://{{ host_name }}{% url verify_account verification_code %}

  Your temporary password is: {{ temp_password }} 

  Use this password to verify your account.
  
  {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

  """
  # template = Section.objects.get(template__key='thank_valued_member_email', category=0)
  txt_template = Template(content)
  html_template = Template('\n'.join(['<p>%s</p>' % x for x in content.split('\n\n') if x]))
  
  if request:
    c = RequestContext( request, {"host_name": request.get_host() if request else "www.vinely.com",
                                  "verification_code": verification_code,
                                  "temp_password": temp_password,
                                  })
  else:
    c = Context({"host_name": request.get_host() if request else "www.vinely.com",
                                  "verification_code": verification_code,
                                  "temp_password": temp_password,
                                  })
  txt_message = txt_template.render(c)
  
  c.update({'sig':True})
  html_message = html_template.render(c)

  # send out verification e-mail, create a verification code
  subject = 'Come visit Vinely website!'
  recipients = [receiver_email]
  if request:
    html_msg = render_to_string("email/base_email_lite.html", RequestContext( request, {'title': subject, 'message': html_message, 'host_name': request.get_host()}))
  else:
    html_msg = render_to_string("email/base_email_lite.html", Context({'title': subject, 'message': html_message, 'host_name': "www.vinely.com"}))

  from_email = 'Welcome to Vinely <welcome@vinely.com>'

  email_log = Email(subject=subject, sender=from_email, recipients=str(recipients), text=txt_message, html=html_msg)
  email_log.save()

  msg = EmailMultiAlternatives(subject, txt_message, from_email, recipients)
  msg.attach_alternative(html_msg, "text/html")
  msg.send()  

def check_zipcode(zipcode):
  '''
  Check provided zipcode against existing ones to verify if vinely operates in the area
  '''
  try:
    code = Zipcode.objects.get(code = zipcode, state__in = SUPPORTED_STATES)
    return True
  except Zipcode.DoesNotExist:
    # application for pro/host?
    return False
