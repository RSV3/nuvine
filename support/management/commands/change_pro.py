from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

from main.models import OrganizedParty, MyHost, Party

class Command(BaseCommand):

  args = ''
  help = 'Switch pro for a party'

  option_list = BaseCommand.option_list + (
    make_option('-t', '--host',
            type='string',
            dest='host',
            default=None,
            help='Host of the party.'),
    make_option('-o', '--oldpro',
            type='string',
            dest='oldpro',
            default=None,
            help='Old pro that originally organized party.'),
    make_option('-n', '--newpro',
            type='string',
            dest='newpro',
            default=None,
            help='New pro that will facilitate the party.'),
    )

  def handle(self, *args, **options):
    if options["host"]:
      host = User.objects.get(email=options["host"])
    else:
      print "Host email is required"
      return

    if options["oldpro"]:
      old_pro = User.objects.get(email=options["oldpro"])

    p = Party.objects.get(host=host)
    org = OrganizedParty.objects.get(party=p)
    if not old_pro:
      old_pro = org.pro

    if old_pro != org.pro:
      print "Something is wrong, old pro is not same as current pro for the party"
      return

    if options["newpro"]:
      new_pro = User.objects.get(email=options["newpro"])
    else:
      print "New pro e-mail is needed"
      return

    org.pro = new_pro
    org.save()

    # update pro host assignment
    myhost = MyHost.objects.filter(host=host).update(pro=new_pro)
