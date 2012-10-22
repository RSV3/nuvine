from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from emailusernames.utils import create_user
from optparse import make_option

import logging

log = logging.getLogger(__name__)

class Command(BaseCommand):
  args = ''
  help = 'Creates a supplier account with email and password'

  option_list = BaseCommand.option_list + (
      make_option('-e', '--email',
          type='string',
          dest='email',
          default=None,
          help='E-mail address for the new account'),
      make_option('-p', '--password',
          type='string',
          dest='password',
          default=None,
          help='Password for new account'),
  )

  def handle(self, *args, **options):

    supplier = Group.objects.get(name="Supplier")

    if options["email"] and options["password"]:
      u = create_user(options["email"], options["password"])
      u.groups.add(supplier)
      u.save()
      log.info("New supplier account with {email} created successfully.".format(email=options['email']))
    else:
      log.error("No email and password supplied.")