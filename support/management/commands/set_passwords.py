from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from optparse import make_option


class Command(BaseCommand):

  args = ''
  help = 'Set all passwords to something (default: hello) for testing'

  option_list = BaseCommand.option_list + (
    make_option('-p', '--password',
            type='string',
            dest='password',
            default=None,
            help='The password to reset to.'),
    )

  def handle(self, *args, **options):
    default_password = "hello"
    if options["password"]:
      default_password = options["password"]

    for u in User.objects.all():
      u.set_password(default_password)
      u.save()

    print "Reset all passwords to: %s" % default_password 