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

    variable, created = Variable.objects.get_or_create(var="{{ host_name }}", description="Host name")
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
    variable, created = Variable.objects.get_or_create(var="{{ host_name }}", description="vinely.com")
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
    variable, created = Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Host name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ invite_host_email }}", description="Host email")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ host_name }}", description="Vinely.com")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
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

    variable, created = Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Vinely.com")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ host_name }}", description="Vinely.com")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
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
    
