"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from cms.models import ContentTemplate, Variable, Section


class SimpleTest(TestCase):
  def runTest(self):
    pass

  def create_web_templates(self):
    self.home_template()
    self.get_started_template()
    self.our_story_template()
    self.how_it_works_template()
    self.vinely_event_template()
    self.rsvp_template()
    self.make_pro_template()
    self.make_host_template()
    self.join_club_template()

  def create_all_templates(self):
    self.create_web_templates()
    self.create_email_templates()

  def create_email_templates(self):
    self.create_verification_email_template()
    self.create_password_change_email_template()
    self.create_account_activation_email_template()
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
    self.create_distribute_thanks_note_email_template()
    self.create_new_party_scheduled_by_host_email_template()
    self.create_host_request_party_email_template()
    self.create_new_party_scheduled_by_host_no_pro_email_template()
    self.create_signed_up_as_host_email_template()
    # self.create_first_time_host_signup_template()
    self.create_new_party_host_confirm_email_template()
    self.create_welcome_email_template()
    self.create_party_setup_completed_email_template()
    self.create_join_the_club_email_template()

  def create_join_the_club_email_template(self):
    content = """

    Welcome to the club! We are delighted you've decided to let Vinely make your wine experience easy, fun, and convenient.
    You're in good hands.

    Your first delicious surprise will arrive within 7 - 10 business days.
    Remember, someone 21 years or older must be available to receive your shipment.

    This first shipment is your Vinely First Taste Experience. It will include 6 wines and an experience booklet.
    As you taste these wines, make sure to record your ratings, and input them to the website by logging into Vinely.com,
    and clicking 'Rate Wines'.

    This will allow us to assign you a wine personality and begin the process of delivering a perfectly personalized selection of wine right to your door each month.
    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """

    template, created = ContentTemplate.objects.get_or_create(key="join_the_club_anon_email", category=0)
    section, created = Section.objects.get_or_create(key='general', template=template)
    section.content = content
    section.save()

  def create_party_setup_completed_email_template(self):
    content = """

    Dear {{ pro_first_name }},

    Your host, {{ party.host.first_name }}, finished setting up the party below on <a href="http://{{ host_name }}">Vinely.com</a>.

    If they haven't yet, please make sure they order a Party Pack and track the RSVPs to ensure they have enough confirmed attendees.
    You can monitor the party details at: <a href="http://{{ host_name }}{% url party_details party.id %}">http://{{ host_name }}{% url party_details party.id %}</a>

    Party: "{{ party.title }}"

    Date: {{ party.event_date|date:"F j, o" }}

    Time: {{ party.event_date|date:"g:i A" }}

    Location: {{ party.address.full_text }}

    If you need to connect with {{ party.host.first_name }}, you can e-mail them at <a href="mailto:{{ party.host.email }}">{{ party.host.email }}</a>{% if host_phone %} or call them at {{ host_phone }}{% endif %}.

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """

    template, created = ContentTemplate.objects.get_or_create(key="party_setup_completed_email", category=0)
    section, created = Section.objects.get_or_create(key='general', template=template)
    section.content = content
    section.save()

    variable, created = Variable.objects.get_or_create(var="{{ pro_first_name }}", description="First name of the Vinely Pro")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.host.first_name }}", description="Name of the party host")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.title }}", description="Name of the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date of the event")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_details party.id %}",
                                                    description="Link to party details page")
    template.variables_legend.add(variable)

  def create_welcome_email_template(self):
    content = """
    Hi {{ taster_first_name }},

    {% if verification_code %}
    To allow you to enjoy all that Vinely has to offer, we have created a new account for you. Follow the following steps to activate your account.
    <h3>Activate Account:</h3>
    <table>
    <tr>
    <td>&nbsp;</td>
    <td><b>Step One</b></td>
    </tr>
    <tr>
    <td>&nbsp;</td>
    <td>Copy your temporary password: {{ temp_password }}</td>
    </tr>
    <tr>
    <td>&nbsp;</td>
    <td><b>Step Two</b></td>
    </tr>
    <tr>
    <td>&nbsp;</td>
    <td>Click the following <a href="http://{{ host_name }}{% url verify_account verification_code %}">link</a> and paste you temporary password to verify your account.</td>
    </tr>
    <tr>
    <td>&nbsp;</td>
    <td><a href="http://{{ host_name }}{% url verify_account verification_code %}">http://{{ host_name }}{% url verify_account verification_code %}</a></td>
    </tr>
    </table>
    {% endif %}

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """
    template, created = ContentTemplate.objects.get_or_create(key="welcome_email", category=0)
    section, created = Section.objects.get_or_create(key='general', template=template)
    section.content = content
    section.save()

    variable, created = Variable.objects.get_or_create(var="{{ taster_first_name }}", description="The taster's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url verify_account verification_code %}", description="Account verification link")
    template.variables_legend.add(variable)

  def create_new_party_host_confirm_email_template(self):
    content = """
    {{ invite_host_name }},

    I'm so excited to lead your Vinely Party on <b>{{ party.event_date|date:"F j, o" }}</b> at <b>{{ party.event_date|date:"g:i A" }}</b>!
    Your party has been scheduled in the system using the information you provided (see below).
    You are now all set to invite your friends and order your tasting kit!

    Party: "{{ party.title }}"

    Date: {{ party.event_date|date:"F j, o" }}

    Time: {{ party.event_date|date:"g:i A" }}

    Location: {{ party.address.full_text }}

    If any changes need to be made, you run into any trouble, or have any questions please contact me at {{ pro_email }}{% if pro_phone %} or {{ pro_phone }}{% endif %}.

    <strong>When you are ready, <a href="http://{{ host_name }}{% url party_add party.id %}">click here</a> to get started.</strong>

    Tastefully,

    - {{ pro_name }}

    """
    template, created = ContentTemplate.objects.get_or_create(key="new_party_host_confirm_email", category=0)
    section, created = Section.objects.get_or_create(key='general', template=template)
    section.content = content
    section.save()

    variable, created = Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Name of the party host")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.title }}", description="Name of the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date of the event")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_email }}", description="Vinely Pro's email address")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_phone }}", description="Vinely Pro's phone number")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_name }}", description="Name of the Vinely Pro")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_add party.id %}",
                                            description="Link to party editing page")
    template.variables_legend.add(variable)

  def create_signed_as_host_email_template_old(self):
    content = """
    We're thrilled about your interest in hosting a Vinely Taste Party!

    {% if pro %}
        You're now a host and can get your party started! Your pro, {{ pro.first_name }}, has been notified and will confirm your party when you complete your setup.
    {% else %}
        To ensure you'll be the host with the most, we'll need to pair you with a Vinely Pro.
        They'll be reaching out soon. If you haven't heard anything within 48 hours, please contact a Vinely Care Specialist at (888) 294-1128 ext 1 or email us.!
    {% endif %}
    In the meantime, you can speed things along by setting up your party now.

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """
    template = ContentTemplate.objects.create(key="signed_up_as_host_email", category=0)
    section, created = Section.objects.create(key='general', template=template)
    section.content = content
    section.save()

    variable, created = Variable.objects.get_or_create(var="{{ host.email }}", description="The Host's email address")
    template.variables_legend.add(variable)

  def create_signed_up_as_host_email_template(self):
    content = """

    We are so excited that you want to host a Vinely Taste Party!

    You have already set up your account. Your login is {{ host.email }}.

    The next step, if you haven't done so already, is to schedule the details of your party.
    Your process is complete when you submit your party for approval by your Vinely Pro.
    (Don't worry if you don't have a Vinely Pro yet, we will find you the perfect Pro to ensure your are the host with the most!).

    Once your pro confirms your party, the invitation will be sent to attendees you have added.
    In the meantime, if you have any questions you can always contact a Vinely Care Specialist at (888)294-1128 ext. 1 or email us at <a href="mailto:care@vinely.com">care@vinely.com</a>.

    PS - Please add <a href="mailto:info@vinely.com">info@vinely.com</a> to your address book to ensure our emails get through!

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """
    template = ContentTemplate.objects.create(key="signed_up_as_host_email", category=0)
    section, created = Section.objects.get_or_create(key='general', template=template)
    section.content = content
    section.save()

    variable, created = Variable.objects.get_or_create(var="{{ host.email }}", description="The Host's email address")
    template.variables_legend.add(variable)

  def create_new_party_scheduled_by_host_no_pro_email_template(self):
    content = """

    Your Vinely Party Request Has Been Submitted!

    Hey {{ party.host.first_name }},

    We're thrilled about your interest in hosting a Vinely Taste Party!You have requested <b>{{ party.title }}</b> to be scheduled on <b>{{ party.event_date|date:"F j, o" }}</b> at <b>{{ party.event_date|date:"g:i A" }}</b>.

    To ensure you'll be the host with the most, we'll need to pair you with a Vinely Pro. You will receive confirmation of this match via email within 48 hours. If any of these details are incorrect, don't worry, your Pro can help you fix it.

    Once your Pro confirms your party, your invitations can go out. Log in any time to see the status of your party or use the link below:

    <a href="http://{{ host_name }}{% url party_details party.id %}">http://{{ host_name }}{% url party_details party.id %}</a>

    If you have any questions, please contact a Vinely Care Specialist via e-mail at <a href="mailto:care@vinely.com">care@vinely.com</a> or by phone at 888-294-1128 ext. 1.

    We look forward to your party!

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """
    template = ContentTemplate.objects.create(key="new_party_scheduled_by_host_no_pro_email", category=0)
    section = Section.objects.create(key='general', template=template)
    section.content = content
    section.save()
    variable, created = Variable.objects.get_or_create(var="{{ party.host.first_name }}", description="Name of the party host")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.title }}", description="Name of the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date of the event")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_details party.id %}",
                                            description="Link to party details page")
    template.variables_legend.add(variable)

  def create_new_party_scheduled_by_host_email_template(self):
    content = """

    Hey {{ invite_host_name }},

    We're thrilled about your interest in hosting a Vinely Taste Party!
    You have requested <b>{{ party.title }}</b> to be scheduled on <b>{{ party.event_date|date:"F j, o" }}</b> at <b>{{ party.event_date|date:"g:i A" }}</b>.

    {% if has_pro %}
        If any of these details are incorrect, don't worry, your Pro, {{ pro_name }}, can help you fix it.
        They can be contacted by email at <a href="mailto:{{ pro.email }}">{{ pro.email }}</a>
        {% if pro_phone %}
            or by phone at {{ pro_phone }}.
        {% endif %}
    {% else %}
        To ensure you'll be the host with the most, we'll need to pair you with a Vinely Pro.
        You will receive confirmation of this match via email within 48 hours.
        If any of these details are incorrect, don't worry, your Pro can help you fix it.
    {% endif %}

    Once your Pro confirms your party, your invitations can go out. Log in any time to see the status of your party or use the link below:

    <a href="http://{{ host_name }}{% url party_details party.id %}">http://{{ host_name }}{% url party_details party.id %}</a>

    If you have any questions, please contact a Vinely Care Specialist via e-mail at <a href="mailto:care@vinely.com">care@vinely.com</a> or by phone at 888-294-1128 ext. 1.

    We look forward to your party!

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

        - The Vinely Team
    """

    template = ContentTemplate.objects.create(key="new_party_scheduled_by_host_email", category=0)
    section = Section.objects.create(key='general', template=template)
    section.content = content
    section.save()
    variable, created = Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Name of the party host")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.title }}", description="Name of the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date of the event")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro.email }}", description="Vinely Pro's email address")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_phone }}", description="Vinely Pro's phone number")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_name }}", description="Name of the Vinely Pro")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_details party.id %}",
                                            description="Link to party details page")
    template.variables_legend.add(variable)

  def create_host_request_party_email_template(self):
    content = """

    Dear {{ pro_name }},

        Your host, {{ invite_host_name }}, is waiting for you to confirm the following party:

    Party: "{{ party.title }}"

    Date: {{ party.event_date|date:"F j, o" }}

    Time: {{ party.event_date|date:"g:i A" }}

    Location: {{ party.address.full_text }}

    {% if party.description %}Party Details: {{ party.description }}{% endif %}

    To confirm the party or make changes, click below:

    <a href="http://{{ host_name }}{% url party_details party.id %}">http://{{ host_name }}{% url party_details party.id %}</a>

    Remember that hosts can't send out their party invitation until you take the next step, so confirm their party now!

    If you need to connect with {{ invite_host_name }}, you can email them at <a href="mailto:{{ party.host.email }}">{{ party.host.email }}</a>{% if host_phone %} or call them at {{ host_phone }}{% endif %}.

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """

    template = ContentTemplate.objects.create(key="host_request_party_email", category=0)
    section = Section.objects.create(key='general', template=template)
    section.content = content
    section.save()
    variable, created = Variable.objects.get_or_create(var="{{ pro_name }}", description="Name of the Vinely Pro")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Name of the party host")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.host.email }}", description="The Host's email address")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ host_phone }}", description="The Host's phone number")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.title }}", description="The name of the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date when event took take place")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.address.full_text }}", description="Address of the event")
    template.variables_legend.add(variable)

  def create_verification_email_template(self):
    content = """

    {% load static %}

    Please verify your e-mail address and create a new password by going to:

    http://{{ host_name }}{% url verify_account verification_code %}

    Your temporary password is: {{ temp_password }}

    Use this password to verify your account.

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    from your Vinely Pros.

    """

    template = ContentTemplate(key="verification_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
    variable, created = Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url verify_account verification_code %}", description="Account verification link")
    template.variables_legend.add(variable)

  def create_password_change_email_template(self):
    content = """

    {% load static %}

    Hey {% if first_name %}{{ first_name }}{% else %}{{ role }}{% endif %}!

    We heard you lost your password. (No prob.  Happens all the time.)

    Here's your temporary password: {{ temp_password }}

    Please update your account with a new password at:

      http://{{ host_name }}{% url verify_account verification_code %}

    Use this password to verify your account and change your password.

    If you don't know why you're receiving this email, click <a href="mailto:care@vinely.com">here</a>.

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """

    template = ContentTemplate(key="password_change_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)

    variable, created = Variable.objects.get_or_create(var="{{ first_name }}", description="User's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ role.name }}", description="User's role e.g. host, pro, taster")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url verify_account verification_code %}", description="Account verification link")
    template.variables_legend.add(variable)

  def create_account_activation_email_template(self):
    content = """

    {% load static %}

    Hey {% if first_name %}{{ first_name }}{% else %}{{ role }}{% endif %}!

    The following information describes how you can get access to Vinely.

    <ul>
    <li>Step 1: Copy the following temporary password {{ temp_password }}</li>
    <li>Step 2: Click the following <a href="http://{{ host_name }}{% url verify_account verification_code %}">link</a> to activate your account.</li>

      http://{{ host_name }}{% url verify_account verification_code %}
    </ul>

    If you don't know why you're receiving this email, you can e-mail us at <a href="mailto:care@vinely.com">care@vinely.com</a>.

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """

    template = ContentTemplate(key="account_activation_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)

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

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}
    
    from your Vinely Pros.

    """
    
    template = ContentTemplate(key="new_invitation_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    from your Vinely Pros

    """

    template = ContentTemplate(key="new_party_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}
    
    Your Tasteful Friends,

    - The Vinely Team 

    """
    template = ContentTemplate(key="pro_request_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

    template = ContentTemplate(key="pro_review_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

    We are so excited that you want to host a Vinely Taste Party!
    You have already set up your account. Your login is {{ host_email }}.

    The next step, if you haven't done so already, is to schedule
    the details of your party. Your process is complete when you
    submit your party for approval by your Vinely Pro. (Don't worry
    if you don't have a Vinely Pro yet, we will find you the perfect
    Pro to ensure your are the host with the most!).

    Once your pro confirms your party, the invitation will be sent
    to attendees you have added. In the meantime, if you have any
    questions you can always contact a Vinely Care Specialist at
    (888) 294-1128 ext. 1 or email us at <a href="mailto:care@vinely.com">email</a>.

    PS- Please add info@vinely.com to your address book to
    ensure our emails get through!


    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """

    template = ContentTemplate(key="know_pro_party_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
    variable, created = Variable.objects.get_or_create(var="{{ host_first_name }}", description="Host's First Name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ host_email }}", description="Host's E-mail")
    template.variables_legend.add(variable)

  def create_unknown_pro_email_template(self):

    content = """

    {% load static %}

    Hey, {{ first_name }}!

    We're thrilled about your interest in hosting a Vinely Taste Party!

    To ensure you'll be the host with the most, we'll need to pair you with a Vinely Pro. They'll be reaching out soon.

    If you haven't heard anything in 48 hours, please contact a Vinely Care Specialist at (888) 294-1128 ext. 1 or <a href="mailto:care@vinely.com">email</a> us. 

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """

    template = ContentTemplate(key="unknown_pro_party_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}
    
    Your Tasteful Friends,

    - The Vinely Team 

    """
    template = ContentTemplate(key="pro_approved_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

      {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

      Your Tasteful Friends,

      - The Vinely Team

    """
    template = ContentTemplate(key="not_in_area_party_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
    variable, created = Variable.objects.get_or_create(var="{{ first_name }}", description="The host's first name")
    template.variables_legend.add(variable)

  def create_order_confirmation_email_template(self):
    content = """
      {% load static %}

      Hey {{ customer }},

      Thank you for choosing Vinely!

      Your order {{ vinely_order_id }} has been received and you should expect your delicious surprise in 7 - 10 business days. Remember, someone 21 years or older must be available to receive your order.

      Keep an eye on your inbox over the next few days, as we will be sending further shipping information.  You can check the status of your order at:

        http://{{ host_name }}{% url order_complete order_id %}

      Happy Tasting!

      {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

      Your Tasteful Friends,

      - The Vinely Team

    """
    template = ContentTemplate(key="order_confirmation_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
    variable, created = Variable.objects.get_or_create(var="{{ customer }}", description="First name of the customer")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ order_id }}", description="Order ID used for the order detail URL")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ vinely_order_id }}", description="Vinely Order ID")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url order_complete order_id %}",
                                                      description="Link to the completed order")
    template.variables_legend.add(variable)

  def create_order_shipped_email_template(self):
    content = """

    {% load static %}

    Dear {% if order.receiver.first_name %}{{ order.receiver.first_name }}{% else %}Valued Customer{% endif %},

    Your order has been shipped and you should receive your order in the next 7 days.  You can check the status of your order at:

      http://{{ host_name }}{% url order_complete order_id %}

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """
    template = ContentTemplate(key="order_shipped_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
    variable, created = Variable.objects.get_or_create(var="{{ order.receiver.first_name }}", description="First name of the customer")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ order_id }}", description="Order ID used for the order detail URL")
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

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team
   
    """
    template = ContentTemplate(key="host_vinely_party_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Vinely Pro {{ pro_first_name }} {{ pro_last_name }}

    """
    template = ContentTemplate(key="new_party_scheduled_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
    variable, created = Variable.objects.get_or_create(var="{{ host_first_name }}", description="Host's first name.")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.title }}", description="The name of the party.")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.description }}", description="Description of the party. Only shown if exists.")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date when event is to take place")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_taster_invite party.id %}", description="Link to the party details")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_email }}", description="Email of the pro that scheduled the party.")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Phone number of the pro. Only shown if exists.")
    template.variables_legend.add(variable)

  def create_distribute_party_invites_email_template(self):
    content = """

    {% load static %}

    What's a Vinely Party? Think of it as learning through drinking.  It's part wine tasting.
    Part personality test.  And part... well... party.

    The wines you'll sample will give us an idea of your personal taste. The flavors you enjoy and the ones you could do without. After sipping, savoring, and rating each wine, we'll assign you one of six Vinely Personalities. Then, we'll be able to send wines perfectly paired to your taste - right to your doorstep.

      Party: "{{ party.title }}"
      Host: {{ invite_host_name }} <{{ invite_host_email }}>
      {% if party.description %}{{ party.description }}{% endif %}
      Date: {{ party.event_date|date:"F j, o" }}
      Time: {{ party.event_date|date:"g:i A" }}
      Location: {{ party.address.full_text }}

    {% if verification_code %}
    To manage your invitation and follow the party, we have created a new account for you.

    Copy this verification code: {{ temp_password }} and click the following link

      http://{{ host_name }}{% url verify_account verification_code %}

    to verify your e-mail address and create a new password.
    {% endif %}

    {% if custom_message %}
    {{ custom_message }}
    {% endif %}

    Will you attend? You know you want to! RSVP by {{ rsvp_date|date:"F j, o" }}. Better yet, don't wait!

    {% if plain %}
    Click on this link to RSVP Now: http://{{ host_name }}{% url party_rsvp rsvp_code party.id %}
    {% else %}
    <div class="email-rsvp-button"><a href="http://{{ host_name }}{% url party_rsvp rsvp_code party.id %}">RSVP Now</a></div>
    {% endif %}

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """
    template = ContentTemplate(key="distribute_party_invites_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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
    variable, created = Variable.objects.get_or_create(var="{{ rsvp_date }}", description="5 days prior to event by which the attendee should RSVP")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_rsvp rsvp_code party.id %}", description="RSVP Link")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Full name of the host that is hosting the party.")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ invite_host_email }}", description="E-mail of the host that is hosting the party.")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="http://{{ host_name }}{% url verify_account verification_code %}", description="E-mail verification link.")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ temp_pssword }}", description="Temporarily created password to verify account.")
    template.variables_legend.add(variable)

  def create_rsvp_thank_you_email_template(self):
    content = """

    {% load static %}

    Hey, {{ first_name }}!

    Guess what? (Drumroll, please.) Your RSVP was received successfully! Now you can prepare to be paired with a Vinely Personality.

    Party: "{{ party.title }}"

    Date: {{ party.event_date|date:"F j, o" }}

    Time: {{ party.event_date|date:"g:i A" }}

    Location: {{ party.address.full_text }}

    Please fill out our quick 11-question survey. It will give us a glimpse into your personal taste. No pressure here. There's no right or wrong answer.

    {% if plain %}
    Click on this link to fill out the questionnaire: http://{{ host_name }}{% url pre_questionnaire_general %}
    {% else %}
    <a class="brand-btn" href="http://{{ host_name }}{% url pre_questionnaire_general %}">Take the First Step</a>
    {% endif %}

    Happy Tasting!

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    - The Vinely Team

    """
    template = ContentTemplate(key="rsvp_thank_you_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

      {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

      - The Vinely Web Site
    """
    template = ContentTemplate(key="contact_request_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    - The Vinely Team

    """
    template = ContentTemplate(key="pro_assigned_notification_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    - The Vinely Team

    """
    template = ContentTemplate(key="mentor_assigned_notification_email", category=0)
    template.save()
    Section.objects.create(key='general', content=content, template=template)
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

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    - The Vinely Team

    """
    template, created = ContentTemplate.objects.get_or_create(key="mentee_assigned_notification_email", category=0)
    section, created = Section.objects.get_or_create(key='general', template=template)
    section.content = content
    section.save()
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

  def create_distribute_thanks_note_email_template(self):
    content = """

    {% load static %}
    Hi {{ taster_first_name }},

    {% if placed_order %}
    Thank you so much for attending my Vinely Taste Party and ordering some wine! I hope you had a great time and you and your personality are getting along great. Don't forget to rate your wines because the more you drink and rate, the better Vinely gets to know you!

    If you'd like to learn about hosting your own Vinely Party, feel free to reach out to our <a href="mailto:{{ pro_email }}">Pro</a> with any questions or to begin planning right away. Hosting has its perks..as a host, you will receive Vinely credit for each sale from your party!

    {% else %}
    Thank you so much for attending my Vinely Taste Party! I hope you had a fantastic time and you and your personality are getting along great!

    It is not too late to place an order. Just sign in at <a href="http://www.vinely.com">Vinely.com</a> to order a personalized selection of wine shipped right to your door. It's easy, convenient, delicious and best of all, guaranteed to please your taste buds!

    And if you join as a Vinely VIP you can enjoy new wines each month, with a continually improving selection based on your feedback ratings. Shipping is free, and you can cancel anytime.

    Remember, your satisfaction isn't just a goal, it's our guarantee!
    {% endif %}

    {{ custom_message }}

    {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

    {% if show_text_sig %}
    Tastefully,

    - {{ party.host.first_name }}
    {% endif %}
    """
    template = ContentTemplate.objects.create(key="distribute_party_thanks_note_email", category=0)
    section, created = Section.objects.get_or_create(key='general', content=content, template=template)
    variable, created = Variable.objects.get_or_create(var="{{ party.title }}", description="The name of the party")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date when event is to take place")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ custom_message }}", description="Optional custom message added to the invite")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ taster_first_name }}", description="The taster's first name")
    template.variables_legend.add(variable)
    variable, created = Variable.objects.get_or_create(var="{{ pro_email }}", description="The Vinely Pro's email address")
    template.variables_legend.add(variable)

  ######################################
  # Web Templates
  ######################################
  def home_template(self):
    content = """
      <h1>WITH VINELY YOU'RE THE WINE EXPERT.</h1>
      <p>Discover your wine personality with friends at a Vinely Taste Party. We'll use that personality to select perfectly paired wine and ship wherever you sip. Interested? </p>

    """
    template = ContentTemplate.objects.create(key="landing_page", category=1)
    Section.objects.create(key='general', content=content, template=template)

  def our_story_template(self):
    content = """
      <h2>Great tastes are hard to come by</h2>

      <p>Our question was simple: Why? Why can't finding tastes you love be easy, social, and fun? Now they are, with Vinely.</p>

      <p>It may look like we have a great time (which we do), but when it comes to taste, we mean business. Serious business. The proof? Our patented Vinely Methodology - a proven system, thoughtfully engineered to define your true Vinely Personality. (It's not rocket science, but it's not far off.)</p>

      <p>At each and every Vinely Taste Party, this methodology is hard at work, separating the Moxies from the Sensational. The Exuberant from the Easygoing. And the Whimsical from the Serendipitous. In turn, you'll be introduced to tastes that fit your Vinely Personality - tastes you won't be able to get enough of.</p>

      <p>We're not out to change the things you enjoy. Fact is, we're here to help you embrace them even more! And with a Vinely Personality, there's nothing stopping you from finding wines that entice, excite, and encourage you to taste Your Personality every chance you get.</p>

      <p>What are you waiting for?</p>
    """
    template = ContentTemplate.objects.create(key="our_story", category=1)
    Section.objects.create(key='general', content=content, template=template)

  def how_it_works_template(self):
    content = """
      <h2>What does Vinely do?</h2>
      <p>By finding your personality, Vinely identifies wines perfectly paired to your taste.
      After all, when it comes to choosing wines you love, who wants to play the guessing game? At a Vinely Taste Party you'll sip, savor, and rate different flavors with your friends.
      Using those ratings, your Vinely Pro will reveal your inner personality. From there, it's hello to happier tastes.</p>

      <h2>How do I order?</h4>
      <p>Once you and your wine personality have had some time to bond, you can easily place an order.
      Then, wines from near and far will show up at your doorstep. The best part? No guesswork. No research. And no intimidating wall of wines.
      Not even a trip to the store. Just exceptional wines, delivered right to your home - conveniently, quickly, and best of all, deliciously.</p>

      <h2>Great! Then what?</h2>
      <p>And since you'll love every wine, every time, we give you a variety of ways to keep fully stocked.
      Become a VIP and receive your personalized Vinely Collection monthly, bi-monthly or quarterly. Or simply place a single order.
      No matter what works for you, we're shipping to wherever you're sipping. All you have to do is ask.</p>

      <h2>Where's the party?</h2>
      <p>If you haven't been invited to a Vinely Taste Party, become a Host and have your own.</p>
    """
    template = ContentTemplate.objects.create(key="how_it_works", category=1)
    Section.objects.create(key='general', content=content, template=template)

  def get_started_template(self):
    general_content = """

      A Vinely Taste Party is a fun, engaging and unique way for you and your friends to learn about the tastes you love.
      As a Vinely Host, we'll pair you with a Vinely Pro. Or you can choose your own.
      They'll help you set up the event, moderate the sampling, and provide each Taster attending with an official Vinely Personality.
      Oh, and did we mention? In addition to a great time, we'll provide you with Vinely Credits you can use toward Vinely merchandise!

    """
    host_content = """

      <h2>Be the host with the most. Follow these simple steps to host your own Vinely Taste Party.</h2>

      <p>Find a space: A living room, loft, porch, or kitchen make great party spots.
      Truthfully, anywhere wine, food, and 8 - 12 people can fit (without throwing a fit) will work perfectly.</p>

      <p><b>Find some time:</b> You and your Vinely Pro will schedule a party date.
      Then, with a little planning, inviting, prepping, and a Vinely Taste Kit, you'll be well on your way to a truly tasteful experience.</p>

      <p><b>Find some friends:</b> You've got 'em. So get 'em to your place!
      For your friends who are wine-tasting veterans, it's sure to be an experience unlike any other they've had.
      For beginners, it's an exciting, no-pressure way to try new tastes and learn what they love.
      Point being, at a Vinely Taste Party, everyone's welcome and everyone wins!</p>

    """

    pro_content = """

      <h2>Want more? Vinely Pro is the way to go!</h2>
      <p>Would you like to conduct Taste Parties and help people find their inner Wine Personality?
      Do you want to earn by helping others learn? By becoming a Vinely Pro, you'll be able to do all that, and more.
      You'll work directly with Vinely Hosts, initiating, scheduling, and conducting Taste Parties.
      You'll be able to start multiple Taste Parties and track each one's progress.
      Become a Pro and there's no telling where the party scene will take you.</p>

      <p>
        Think you have what it takes to get the Taste Party started?
      </p>

    """
    template = ContentTemplate.objects.create(key="get_started", category=1)
    Section.objects.create(key='general', content=general_content, template=template)
    Section.objects.create(key='host', content=host_content, template=template)
    Section.objects.create(key='pro', content=pro_content, template=template)

  def vinely_event_template(self):
    general_content = """

    Join us October 10th, 2012 for a Vinely Taste Party open house from 4:00 pm to 7:00 pm in downtown Grand Rapids
    at the <a href="http://www.shopmodiv.com/floorplan.html">Haworth|Interphase Showroom space</a> located on the
    corner of Monroe Center and Division.

    <h2>WHAT'S A VINELY TASTE PARTY?</h2>
    <p>Think of it as learning through drinking. It's part wine tasting. Part personality test. And part...well...party.</p>

    <p>The wines you'll sample will give us an idea of your personal taste. The flavors you enjoy and the ones you
    could do without. After sipping, savoring, and rating each wine, we'll assign you one of six Vinely Personalities.
    Then, we'll be able to send wines perfectly paired to your taste - right to your doorstep.</p>

    <p>Come early, stay late but promise you will come.</p>

    <p>Tell us you'll attend! You know you want to!</p>

    <p>By filling out the information below, an online profile will be created for you and gets you one step closer to
    finding out your Vinely Wine Personality.</p>
    <br />
    {% if fb_view %}
      <a class="btn btn-large btn-success" href="/facebook/event/signup/8/">Sign Me Up</a>
    {% else %}
      <a class="btn btn-large btn-success" href="/event/signup/8/">Sign Me Up</a>
    {% endif %}
    <br /><br />

    <h2>But where's the parking?</h2>
    <p>Don't let parking stand in your way. There are lots of meters, most of which are free after 6:00 pm.
    If you arrive before 6:00 pm you can get an hour free in the Monroe Center lot located at 37 Ionia Avenue Northwest
    (on the corner of Ionia ave and Louis)</p>
    <h2>Questions</h2>
    <p>Contact a Vinely Care Specialist at <a href="care@vinely.com">care@vinely.com</a> or call 1.888.294.1128 ext: 1</p>

    """
    template = ContentTemplate.objects.create(key="vinely_event", category=1)
    Section.objects.create(key='general', content=general_content, template=template)

  def rsvp_template(self):
    general_content = """

    <p>What's a Vinely Taste Party? Think of it as learning through drinking.
    It's part wine tasting. Part personality test. And part...well...party.</p>

    <p>The wines you'll sample will give us an idea of your personal taste.
    The flavors you enjoy and the ones you could do without.
    After sipping, savoring, and rating each wine, we'll assign you one of six Vinely Personalities.
    Then, we'll be able to send wines perfectly paired to your taste - right to your doorstep.</p>
    """
    template = ContentTemplate.objects.create(key="rsvp", category=1)
    Section.objects.create(key='general', content=general_content, template=template)


  def make_pro_template(self):
    host_header = 'Where\'s the wine party? Your place!'
    host_sub_header = '<span></span>'

    content_overview = """
    <p>You're social and you love wine. Why not benefit by having the Vinely Experience in your home?</p>

    <p>Signup to host a party and one of our carefully trained experts, or as we call them, our Vinely Pros,
    will handle the heavy lifting. Isn't it great when you can enjoy your own party?</p>

    <p>Your friends will think you're the host with the most when you introduce them to their Wine Personality.</p>
    """

    content_people = """
    <p>Think friends, relatives, neighbors, co-workers...anyone over 21 who likes wine and a good time.</p>
    """

    content_place = """
    <p>Staying in is the new going out with Vinely.</p>
    <p>Enjoy your Vinely experience anywhere so long as you can fit 12 people.
    Any night can be turned into time with friends, a corporate retreat or a neighbourhood gathering.</p>
    """

    content_rewards = """
    <p>Lots and lots of rewards!!!</p>
    """

    content_order = """
    <p>
    Order your tasting experience ($99) which includes 6 bottles of wine and other tasting supplies.
    This should be ordered 2 weeks prior to the party to ensure plenty of time to choose music and food for your party
    (artisan, crackers, stuffed mushrooms, best of the 80's?)
    </p>
    """

    template, created = ContentTemplate.objects.get_or_create(key="make_pro", category=1)
    section, created = Section.objects.get_or_create(key="general", template=template)
    section.content = content_overview
    section.save()
    section, created = Section.objects.get_or_create(key='header', template=template)
    section.content = host_header
    section.save()
    section, created = Section.objects.get_or_create(key='sub_header', template=template)
    section.content = host_sub_header
    section.save()
    section, created = Section.objects.get_or_create(key="people", template=template)
    section.content = content_people
    section.save()
    section, created = Section.objects.get_or_create(key="place", template=template)
    section.content = content_place
    section.save()
    section, created = Section.objects.get_or_create(key="rewards", template=template)
    section.content = content_rewards
    section.save()
    section, created = Section.objects.get_or_create(key="order", template=template)
    section.content = content_order
    section.save()

  def make_host_template(self):
    host_header = 'Where\'s the wine party? Your place!'
    host_sub_header = '<span></span>'
    content_overview = """
    <p>You're social and you love wine. Why not benefit by having the Vinely Experience in your home?</p>

    <p>Signup to host a party and one of our carefully trained experts, or as we call them, our Vinely Pros,
    will handle the heavy lifting. Isn't it great when you can enjoy your own party?</p>

    <p>Your friends will think you're the host with the most when you introduce them to their Wine Personality.</p>
    """

    content_people = """
    <p>Think friends, relatives, neighbors, co-workers...anyone over 21 who likes wine and a good time.</p>
    """

    content_place = """
    <p>Staying in is the new going out with Vinely.</p>
    <p>Enjoy your Vinely experience anywhere so long as you can fit 12 people.
    Any night can be turned into time with friends, a corporate retreat or a neighbourhood gathering.</p>
    """

    content_rewards = """
    <p>Lots and lots of rewards!!!</p>
    """

    content_order = """
    <p>
    Order your tasting experience ($99) which includes 6 bottles of wine and other tasting supplies.
    This should be ordered 2 weeks prior to the party to ensure plenty of time to choose music and food for your party
    (artisan, crackers, stuffed mushrooms, best of the 80's?)
    </p>
    """

    template, created = ContentTemplate.objects.get_or_create(key="make_host", category=1)
    section, created = Section.objects.get_or_create(key='header', template=template)
    section.content = host_header
    section.save()
    section, created = Section.objects.get_or_create(key='sub_header', template=template)
    section.content = host_sub_header
    section.save()
    section, created = Section.objects.get_or_create(key="overview", template=template)
    section.content = content_overview
    section.save()
    section, created = Section.objects.get_or_create(key="people", template=template)
    section.content = content_people
    section.save()
    section, created = Section.objects.get_or_create(key="place", template=template)
    section.content = content_place
    section.save()
    section, created = Section.objects.get_or_create(key="rewards", template=template)
    section.content = content_rewards
    section.save()
    section, created = Section.objects.get_or_create(key="order", template=template)
    section.content = content_order
    section.save()

  def join_club_template(self):
    host_header = 'Treat yourself to a club that\'s all about you'
    host_sub_header = '<span></span>'
    content_overview = """
    <p>Say hello to a future of wine that you are guaranteed to leave.</p>

    <p>Join the exclusive Vinely club to learn your Wine Personality,
    gain access to member-only perks and receive delicious personalized,
    hand-picked wine delivered to your door every month</p>

    <p>Your friends will think you're the host with the most when you introduce them to their Wine Personality.</p>
    """

    content_anticipition = """
    <p>Are you Whimsical, Exuberant, Sensational, Moxie, Easygoing or Serendipitous? If you don't know, get drinking!</p>
    <p>Just sip and rate our 6 carefully selected First Taste Wines to uncover your Vinely Wine Personality.</p>
    """

    content_surprise = """
    <p>Who doesn't love a surprise, especially when you are guaranteed to love it?
    As a Vinely Club member you will eagerly await 6 different wines perfectly matched to your taste-buds.
    Enhance your enjoyment every month with wine you love. One more surprise from us...we pay for shipping!</p>
    <p>This is a club where the deliveries are as unique as you!</p>
    """

    content_indulgence = """
    <p>You will be the envy of all your friends when every glass you pour is one you love.
    Give yourself the gift of easy wine enjoyment. Go ahead, you deserve it.</p>
    """

    content_excitement = """
    <p>
    Enjoy perks like member-only experiences, preview events, trips, gifts and items that express your personality.
    </p>
    """

    content_product = """
    <p>
      <ul id="membership">
        <li>6 unique bottles of wine each month</li>
        <li>Delivery right to your door, FREE</li>
        <li>Continually improving wines based on your ratings</li>
        <li>Satisfaction guaranteed. Period. Or your money back</li>
        <li>No risk. Cancel anytime, no questions asked!</li>
      </ul>
    </p>
    """

    template, created = ContentTemplate.objects.get_or_create(key="join_club", category=1)
    section, created = Section.objects.get_or_create(key='header', template=template)
    section.content = host_header
    section.save()
    section, created = Section.objects.get_or_create(key='sub_header', template=template)
    section.content = host_sub_header
    section.save()
    section, created = Section.objects.get_or_create(key="overview", template=template)
    section.content = content_overview
    section.save()
    section, created = Section.objects.get_or_create(key="anticipation", template=template)
    section.content = content_anticipition
    section.save()
    section, created = Section.objects.get_or_create(key="surprise", template=template)
    section.content = content_surprise
    section.save()
    section, created = Section.objects.get_or_create(key="indulgence", template=template)
    section.content = content_indulgence
    section.save()
    section, created = Section.objects.get_or_create(key="excitement", template=template)
    section.content = content_excitement
    section.save()
    section, created = Section.objects.get_or_create(key="product", template=template)
    section.content = content_product
    section.save()
