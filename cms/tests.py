"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cms.models import ContentTemplate, Variable

class SimpleTest(TestCase):
  def runTest(self):
    pass

  def create_web_templates(self):
    pass

  def create_all_templates(self):
      self.create_web_templates()
      self.create_email_templates()

  def create_email_templates(self):
    self.create_verification_email_template()
    self.create_password_change_email_template()
    self.create_new_invitation_email_template()
    self.create_new_party_email_template()
    self.create_pro_request_email_template()
    self.create_pro_review_email_template()
    self.create_know_pro_party_email_template()
    self.create_unknown_pro_email_template()
    self.create_pro_approved_email_template()
    self.create_not_in_area_party_email_template()
    self.create_order_confirmation_email_template()
    self.create_order_shipped_email_template()
    self.create_host_vinely_party_email_template()
    self.create_new_party_scheduled_email_template()
    self.create_distribute_party_invites_email_template()
    self.create_rsvp_thank_you_email_template()
    self.create_contact_request_email_template()
    self.create_pro_assigned_notification_email_template()
    self.create_mentor_assigned_notification_email_template()
    self.create_mentee_assigned_notification_email_template()


  def create_verification_email_template(self):
    content = """

    {% load static %}

    Please verify your e-mail address and create a new password by going to:

    http://{{ host_name }}{% url verify_account verification_code %}

    Your temporary password is: {{ temp_password }} 

    Use this password to verify your account.

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    from your Vinely Pros.

    """

    template = ContentTemplate(key="verification_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url verify_account verification_code %}", description="Account verification link")
    template.variables_legend.add(variable)    

  def create_password_change_email_template(self):
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
    
    template = ContentTemplate(key="password_change_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ first_name }}", description="User's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ role.name }}", description="User's role e.g. host, pro, taster")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url verify_account verification_code %}", description="Account verification link")
    template.variables_legend.add(variable)

  def create_new_invitation_email_template(self):
    content = """

    {% load static %}

    You have been invited to a Vinely Party [{{ party_name }}] by {{ invite_host_name }} ({{ invite_host_email }}).
    We have automatically created a new account for you.

    Please verify your e-mail address and create a new password by going to:

      http://{{ host_name }}{% url verify_account verification_code %}

    Your temporary password is: {{ temp_password }} 

    Use this password to verify your account.


    You will receive an invitation soon, but you can go ahead and RSVP to above party invitation at:

      http://{{ host_name }}{% url party_rsvp party_id %}

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}
    
    from your Vinely Pros.

    """
    
    template = ContentTemplate(key="new_invitation_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ party_name }}", description="Name of the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Name of the party host")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ invite_host_email }}", description="Email of the party host")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url verify_account verification_code %}", description="Account verification link")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_rsvp party_id %}", description="RSVP link")
    template.variables_legend.add(variable)    

  def create_new_party_email_template(self):
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

    template = ContentTemplate(key="new_party_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Name of the party host")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url verify_account verification_code %}", description="Account verification link")
    template.variables_legend.add(variable)

  def create_pro_request_email_template(self):
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
    template = ContentTemplate(key="pro_request_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ first_name }}", description="First name")
    template.variables_legend.add(variable)

  def create_pro_review_email_template(self):
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

    template = ContentTemplate(key="pro_review_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ first_name }}", description="Pro's First name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ last_name }}", description="Pro's Last name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ email }}", description="Pro's Email")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ zipcode }}", description="Pro's zipcode")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ phone }}", description="Pro's phone number. Only shown if available")
    template.variables_legend.add(variable)

  def create_know_pro_party_email_template(self):
    content = """

    {% load static %}

    Hey {{ host_first_name }}!

    We're thrilled about your interest in hosting a Vinely Taste Party!  
    Since you already have a Vinely Pro in mind, they will soon be in contact to set a date and time.
    If you haven't heard anything in 48 hours, please contact a Vinely Care Specialist at:

      (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """

    template = ContentTemplate(key="know_pro_party_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ host_first_name }}", description="Host's First name")
    template.variables_legend.add(variable)

  def create_unknown_pro_email_template(self):

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

    template = ContentTemplate(key="unknown_pro_party_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ first_name }}", description="Host's First name")
    template.variables_legend.add(variable)

  def create_pro_approved_email_template(self):

    content = """

    {% load static %}

    Hey {{ applicant.first_name }},<br>

    Your application to become Vinely Pro has been approved.  

    Your Pro account number is {{ pro_account_number }}. Please keep that for future reference.

    You may now login to your account and start recruiting hosts for your taste parties!

    Go have some fun wine parties!

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}
    
    Your Tasteful Friends,

    - The Vinely Team 

    """
    template = ContentTemplate(key="pro_approved_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ applicant.first_name }}", description="The first name of the approved pro")
    template.variables_legend.add(variable)

  def create_not_in_area_party_email_template(self):
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
    template = ContentTemplate(key="not_in_area_party_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ first_name }}", description="The host's first name")
    template.variables_legend.add(variable)

  def create_order_confirmation_email_template(self):
    content = """
      {% load static %}

      Hey {{ customer }},

      Thank you for choosing Vinely!

      Your order {{ order_id }} has been received and you should expect your delicious surprise in 7 - 10 business days. Remember, someone 21 years or older must be available to receive your order.

      Keep an eye on your inbox over the next few days, as we will be sending further shipping information.  You can check the status of your order at:

        http://{{ host_name }}{% url order_complete order_id %}

      Happy Tasting!

      {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

      Your Tasteful Friends,
    
      - The Vinely Team

    """
    template = ContentTemplate(key="order_confirmation_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ customer }}", description="First name of the customer")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ order_id }}", description="Order ID")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url order_complete order_id %}", 
                                                      description="Link to the completed order")
    template.variables_legend.add(variable)

  def create_order_shipped_email_template(self):
    content = """

    {% load static %}

    Dear {% if order.receiver.first_name %}{{ order.receiver.first_name }}{% else %}Valued Customer{% endif %},

    Your order has been shipped and you should receive your order in the next 7 days.  You can check the status of your order at:

      http://{{ host_name }}{% url order_complete order.order_id %}

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """
    template = ContentTemplate(key="order_shipped_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ order.receiver.first_name }}", description="First name of the customer")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ order_id }}", description="Order ID")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url order_complete order_id %}", 
                                                      description="Link to the completed order")
    template.variables_legend.add(variable)

  def create_host_vinely_party_email_template(self):
    content = """

    {% load static %}

    Hey {{ pro_first_name }}!

    Guess what? (Drumroll, please.) Someone in your area would like to be a host at a Vinely Taste Party! Please follow up ASAP to help set up an event date, make recommendations, and answer any possible questions.

    Name: {{ first_name }} {{ last_name }}

    Email Address: {{ email }} 

    {% if phone %}
    Phone: {{ phone }}
    {% endif %}

    Zipcode: {{ zipcode }}

    If you have any questions, please contact a Vinely Care Specialist at (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team
   
    """
    template = ContentTemplate(key="host_vinely_party_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ pro_first_name }}", description="First name of the Vinely Pro")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ first_name }}", description="Host's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ last_name }}", description="Host's last name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ email }}", description="Host's email")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ phone }}", description="Host's phone - only shown if it exists")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ zipcode }}", description="Host's zipcode")
    template.variables_legend.add(variable)

  def create_new_party_scheduled_email_template(self):
    content = """

    {% load static %}

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

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    Your Vinely Pro {{ pro_first_name }} {{ pro_last_name }}

    """
    template = ContentTemplate(key="new_party_scheduled_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ host_first_name }}", description="Host's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.title }}", description="The name of the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.description }}", description="Description of the party. Only shown if exists")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date when event is to take place")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_taster_invite party.id %}", description="Link to the party details")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_email }}", description="Email of the pro that scheduled the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Phone number of the pro. Only shown if exists")
    template.variables_legend.add(variable)

  def create_distribute_party_invites_email_template(self):
    content = """

    {% load static %}

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

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """
    template = ContentTemplate(key="distribute_party_invites_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ party.title }}", description="The name of the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.description }}", description="Description of the party. Only shown if exists")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date when event is to take place")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.address.full_text }}", description="Address of the event")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ custom_message }}", description="Optional custom message added to the invite")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_rsvp party.id %}", description="RSVP Link")
    template.variables_legend.add(variable)

  def create_rsvp_thank_you_email_template(self):
    content = """

    {% load static %}

    Hey, {{ first_name }}!

    Guess what? (Drumroll, please.) Your RSVP was received successfully! Now you can prepare to be paired with a Vinely Personality.

    Please fill out our quick 11-question survey. It will give us a glimpse into your personal taste. No pressure here. There's no right or wrong answer.

    {% if plain %}
    Click on this link to fill out the questionnaire: http://{{ host_name }}{% url pre_questionnaire_general %}
    {% else %}
    <a class="brand-btn" ref="http://{{ host_name }}{% url pre_questionnaire_general %}">Take the First Step</a>
    {% endif %}

    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    - The Vinely Team

    """
    template = ContentTemplate(key="rsvp_thank_you_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ first_name }}", description="The invitee's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url pre_questionnaire_general %}", description="Link to the tasting questionnaire")
    template.variables_legend.add(variable)

  def create_contact_request_email_template(self):
    content = """

    {% load static %}

    {% if contact_request.first_name %}{{ contact_request.first_name }} {{ contact_request.last_name }}{% else %}Potential Customer{% endif %}, is interested in Vinely.  Please reach out via

      E-mail: {{ contact_request.email }}
      Phone: {{ contact_request.phone }}

    Following message was submitted:

      Subject: {{ contact_request.subject }}

      {{ contact_request.message }}

      {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

      - The Vinely Web Site
    """
    template = ContentTemplate(key="contact_request_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ contact_request.first_name }}", description="First name of the user (Optional)")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ contact_request.last_name }}", description="Last name of the user (Optional)")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ contact_request.email }}", description="User's email")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ contact_request.phone }}", description="User's phone")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ contact_request.subject }}", description="Subject of the request")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ contact_request.message }}", description="Message content of the request")
    template.variables_legend.add(variable)

  def create_pro_assigned_notification_email_template(self):
    content = """

    {% load static %}

    Dear {% if host_user.first_name %}{{ host_user.first_name }} {{ host_user.last_name }}{% else %}Friendly Host{% endif %},

    A new Vinely Pro has been assigned to you and now you may request to host Vinely parties! Here's your Vinely Pro contact information:

    Name: {{ pro_user.first_name }} {{ pro_user.last_name }}
    E-mail: {{ pro_user.email }}
    Phone: {{ pro_user.get_profile.phone }} 

    Please reach out to your Pro and start your Vinely parties!

    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    - The Vinely Team

    """
    template = ContentTemplate(key="pro_assigned_notification_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ host_user.first_name }}", description="Host's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ host_user.last_name }}", description="Host's last name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_user.first_name }}", description="Pro's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_user.last_name }}", description="Pro's last name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_user.get_profile.phone }}", description="Pro's phone number")
    template.variables_legend.add(variable)

  def create_mentor_assigned_notification_email_template(self):
    content = """

    {% load static %}

    Dear {% if mentee.first_name %}{{ mentee.first_name }} {{ mentee.last_name }}{% else %}Friend{% endif %},

    A new Vinely Mentor has been assigned to you so if you need any help reach out to the Mentor! Here's your Vinely Mentor contact information:

    Name: {{ mentor.first_name }} {{ mentor.last_name }}
    E-mail: {{ mentor.email }}
    Phone: {{ mentor.get_profile.phone }} 

    Please reach out to your Mentor if you need help! 

    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    - The Vinely Team

    """
    template = ContentTemplate(key="mentor_assigned_notification_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ mentee.first_name }}", description="Mentee's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ mentee.last_name }}", description="Mentee's last name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ mentor.first_name }}", description="Mentor's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ mentor.last_name }}", description="Mentor's last name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ mentor.email }}", description="Mentor's email")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ mentor.get_profile.phone }}", description="Mentor's phone number")
    template.variables_legend.add(variable)

  def create_mentee_assigned_notification_email_template(self):
    content = """

    {% load static %}

    Dear {% if mentor.first_name %}{{ mentor.first_name }} {{ mentor.last_name }}{% else %}Friend{% endif %},

    A new Vinely Mentee has been assigned to you so please help them when needed! Here's your Vinely Mentee contact information:

    Name: {{ mentee.first_name }} {{ mentee.last_name }}
    E-mail: {{ mentee.email }}
    Phone: {{ mentee.get_profile.phone }} 

    Please reach out to your Mentee to share your wisdom! 

    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    - The Vinely Team

    """
    template = ContentTemplate(key="mentee_assigned_notification_email", content=content, category=0)
    template.save()

    variable, created = Variable.objects.get_or_create(var="{{ mentor.first_name }}", description="Mentor's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ mentor.last_name }}", description="Mentor's last name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ mentee.first_name }}", description="Mentee's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ mentee.last_name }}", description="Mentee's last name")
    template.variables_legend.add(variable)    
    variable, created = Variable.objects.get_or_create(var="{{ mentee.email }}", description="Mentee's email")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ mentee.get_profile.phone }}", description="Mentee's phone number")
    template.variables_legend.add(variable)
