from django.core.mail import send_mail
from django.template import Context, Template


def send_order_confirmation_email(request, order_id, receiver_email):

    message_template = Template("""

    Dear {{ customer }},

    Thank you for ordering at Vinely. 

    We will soon be processing your order and you should receive your orders in 7 days. 

    You can check the status of your order at:

    http://{{ host_name }}{% url order_complete order_id %}


    """)

    c = Context({"customer": request.user.first_name if request.user.first_name else "Valued Customer", 
                "host_name": request.get_host(),
                "order_id": order_id}) 
    message = message_template.render(c)

    # send out verification e-mail, create a verification code
    send_mail('Order Confirmation from Vinely!', message, 'support@vinely.com', [receiver_email])


