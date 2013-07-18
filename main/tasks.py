from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.http import HttpRequest
from django.db import models

from celery import task, current_app, Task

from support.models import Email
from main.models import PartyInvite, Party, Order, ThankYouNote, ModelTask
from main.utils import distribute_party_thanks_note_email
import logging
logger = logging.getLogger(__name__)


class CustomTask(Task):
  '''
  Overrides task decorator to allow tracking tasks based on object instance
  '''
  def exists_for(self, instance):
    '''
    Check if a celery task already exists for this instance
    '''
    return ModelTask.filter(self, instance).exists()

  def terminate(self, instance):
    tasks = ModelTask.filter(self, instance)
    for task in tasks:
      current_app.control.revoke(task.task_id)
      logger.info("Terminated task %s" % task.task_id)
    tasks.delete()

  def apply_async(self, *args, **kwargs):
    '''
    Override ``apply_sync`` to allow you to create a model task object
    '''
    instance = kwargs.pop('instance', None)
    async_result = super(CustomTask, self).apply_async(*args, **kwargs)

    if instance and not self.exists_for(instance):
      ModelTask.create(async_result, instance)
    return async_result

  def AsyncResult(self, *args, **kwargs):
    if args and isinstance(args[0], models.Model) and \
        self.exists_for(args[0]):
      task_id = ModelTask.filter(self, args[0])[0].task_id
      return super(CustomTask, self).AsyncResult(task_id)
    else:
      return super(CustomTask, self).AsyncResult(*args, **kwargs)


def model_task(*args, **kwargs):
  # return current_app.task(*args, **dict({'accept_magic_kwargs': False,
  #                                        'base': CustomTask}, **kwargs))
  return task(*args, base=CustomTask, **kwargs)


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


@model_task
def schedule_thank_notes(party):
  try:
    party = Party.objects.get(pk=party.id)

    request = HttpRequest()
    request.META['SERVER_NAME'] = "www.vinely.com"
    request.META['SERVER_PORT'] = 80
    request.user = party.host
    request.session = {}

    note_sent = ThankYouNote.objects.create(party=party)
    invitees = PartyInvite.objects.filter(party=party).exclude(invitee=party.host)
    orders = Order.objects.filter(cart__party=party)
    buyers = invitees.filter(invitee__in=[x.receiver for x in orders])
    non_buyers = invitees.exclude(invitee__in=[x.receiver for x in orders])
    if non_buyers:
      distribute_party_thanks_note_email(request, note_sent, non_buyers, placed_order=False)
    if buyers:
      distribute_party_thanks_note_email(request, note_sent, buyers, placed_order=True)
  except Party.DoesNotExist:
    pass
