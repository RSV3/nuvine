from django.core.mail import send_mail
from django.template import Context, Template

def send_verification_email(request, verification_code, temp_password, receiver_email):

    message_template = Template("""

    Please verify your e-mail address and create a new password by going to:

    http://{{ host_name }}{% url verify_account verification_code %}

    Your temporary password is: {{ temp_password }} 

    Use this password to verify your account.

    """)

    c = Context({"host_name": request.get_host(),
                "verification_code": verification_code,
                "temp_password": temp_password})
    message = message_template.render(c)

    # send out verification e-mail, create a verification code
    send_mail('Welcome to Vinely!', message, 'support@vinely.com', [receiver_email])

def send_new_invitation_email(request, verification_code, temp_password, party_invite):

    message_template = Template("""

    You have been invited to Vinely Party [{{ party_name }}] 
    by {{ invite_host_name }} ({{ invite_host_email }}).

    Please verify your e-mail address and create a new password by going to:

    http://{{ host_name }}{% url verify_account verification_code %}

    Your temporary password is: {{ temp_password }} 

    Use this password to verify your account.


    You need to also RSVP to your party invitation at:

    http://{{ host_name }}{% url party_rsvp %}

    """)

    c = Context({"party_name": party_invite.party.title, 
                "invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
                "invite_host_email": request.user.email,
                "host_name": request.get_host(),
                "verification_code": verification_code,
                "temp_password": temp_password})
    message = message_template.render(c)

    # send out verification e-mail, create a verification code
    send_mail('Join Vinely Party!', message, 'support@vinely.com', [party_invite.invitee.email])

def send_party_invitation_email(request, party_invite):

    message_template = Template("""

    You have been invited to Vinely Party [{{ party_name }}] 
    by {{ invite_host_name }} ({{ invite_host_email }}).


    You need to also RSVP to your party invitation at:

    http://{{ host_name }}{% url party_rsvp %}

    """)

    c = Context({"party_name": party_invite.party.title,
                "invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
                "invite_host_email": request.user.email,
                "host_name": request.get_host()})
    message = message_template.render(c)

    # send out verification e-mail, create a verification code
    send_mail('Join Vinely Party!', message, 'support@vinely.com', [party_invite.invitee.email])


def send_new_party_email(request, verification_code, temp_password, receiver_email):

    message_template = Template("""

    You have been invited to host a new Vinely party by {{ invite_host_name }} ({{ invite_host_email }}).

    Please verify your e-mail address and create a new password by going to:

    http://{{ host_name }}{% url verify_account verification_code %}

    Your temporary password is: {{ temp_password }} 

    Use this password to verify your account.

    """)

    c = Context({"invite_host_name": "%s %s"%(request.user.first_name, request.user.last_name),
                "invite_host_email": request.user.email,
                "host_name": request.get_host(),
                "verification_code": verification_code,
                "temp_password": temp_password})
    message = message_template.render(c)

    # send out verification e-mail, create a verification code
    send_mail('Welcome to Vinely!', message, 'support@vinely.com', [receiver_email])


