
from django.core.management.base import BaseCommand
from optparse import make_option

from cms.tests import SimpleTest
from cms.models import ContentTemplate

import sys
class Command(BaseCommand):
  help = "Initialize email and web templates"

  option_list = BaseCommand.option_list + (
    make_option('-e', '--email',
            action='store_true',
            dest='email',
            default=False,
            help='Recreate only the email templates'),

    make_option('-w', '--web',
            action='store_true',
            dest='web',
            default=False,
            help='Recreate only the web templates'),
    )

  def handle(self, *args, **options):
    # msg = ("\nThis will delete all changes that have ever been made on the templates "
    #         "\nAre you sure you want to proceed? (yes/no): ")
    # confirm = input(msg)
    # while 1:
    #     if confirm not in ('yes', 'no'):
    #         confirm = input('Please enter either "yes" or "no": ')
    #         continue
    #     if confirm == 'no':
    #         return
    #     break
    
    s = SimpleTest()
    if options['email']:
      print "Recreating email templates"
      emails = ContentTemplate.objects.filter(category=ContentTemplate.TEMPLATE_TYPE[0][0])
      if emails:
        emails.variables_legend.delete()
        emails.delete()
      s.create_email_templates()
    elif options['web']:
      print "Recreating web templates"
      web = ContentTemplate.objects.filter(category=ContentTemplate.TEMPLATE_TYPE[0][1])
      if web:
        web.variables_legend.delete()
        web.delete()
      s.create_web_templates()
    else:
      print "Recreating all templates"
      both = ContentTemplate.objects.all().delete()
      if both:
        both.variables_legend.delete()
        both.delete()
      s.create_all_templates()

