from django.core.mail import EmailMultiAlternatives
from celery import task
from support.models import Email
from django.conf import settings

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
