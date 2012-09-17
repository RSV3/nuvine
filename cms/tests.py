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

    Your application to become Vinely Pro has been approved.  You may now login to your account
    and start recruiting hosts for your taste parties!

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