from django.core.mail import EmailMultiAlternatives
from celery import task
from support.models import Email
from django.conf import settings

# from main.models import PartyInvite, Party, Order, ThankYouNote
# from main.utils import distribute_party_thanks_note_email

import logging
logger = logging.getLogger(__name__)


@task
def async_send_mail(email_id, headers=None):
  email = sync_send_mail(email_id, headers)
  logger.info('Async send mail %s' % email)
  return email_id


def sync_send_mail(email_id, headers=None):
  email = Email.objects.get(id=email_id)
  recipients = eval(email.recipients)
  msg = EmailMultiAlternatives(email.subject, email.text, email.sender, recipients, headers=headers)
  msg.attach_alternative(email.html, "text/html")
  msg.send()
  return email


def task_send_mail(email_id, headers=None):
  if settings.USE_CELERY:
    async_send_mail.delay(email_id, headers=None)
  else:
    sync_send_mail(email_id, headers=None)


# @task
# def schedule_thank_notes(request, party_id):
#   # problem using celery task:
#   # keeping track when user updates or deletes from main app or from admin
#   try:
#     party = Party.objects.get(pk=party_id)

#     note_sent = ThankYouNote.objects.create(party=party)
#     invitees = PartyInvite.objects.filter(party=party).exclude(invitee=party.host)
#     orders = Order.objects.filter(cart__party=party)
#     buyers = invitees.filter(invitee__in=[x.receiver for x in orders])
#     non_buyers = invitees.exclude(invitee__in=[x.receiver for x in orders])
#     if non_buyers:
#       distribute_party_thanks_note_email(request, note_sent, non_buyers, placed_order=False)
#     if buyers:
#       distribute_party_thanks_note_email(request, note_sent, buyers, placed_order=True)
#   except Party.DoesNotExist:
#     pass
