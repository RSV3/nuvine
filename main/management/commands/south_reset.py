from optparse import make_option
from os.path import dirname, join, abspath, basename
import shutil
import subprocess
from django.core.management.base import AppCommand

"""
    From: http://balzerg.blogspot.co.il/2012/09/django-app-reset-with-south.html
"""


class Command(AppCommand):
  help = "Reset south migrations for app"
  option_list = AppCommand.option_list + (
      make_option('--soft',
          action = 'store_true',
          dest = 'soft',
          default = False,
          help = "Just merge the migrations and update the south DB accordingly, doesn't change actual app tables"),
      make_option('--database',
          action = 'store',
          dest = 'database',
          default = 'default',
          help = 'Nominates a database to synchronize. Defaults to the "default" database.'),
      )

  def handle_app(self, app, soft = False, verbosity = 1, **options):
    printer = Printer(verbosity = verbosity)

    def manage_call(*a, **kw):
      b = ['--%s%s' % (key, ('=' + value) if value != True else '') for key, value in kw.iteritems() if value != False]
      final_args = ['python', 'manage.py'] + list(a) + b
      printer('Calling: ' + ' '.join(final_args), 3)
      return subprocess.call(final_args)

    app_name = basename(dirname(app.__file__))
    printer('Resetting %s (%s)' % (app_name, 'soft' if soft else 'hard'))
    migrations_dir = abspath(join(dirname(app.__file__), 'migrations'))
    printer('Rolling back migrations', 2)
    manage_call('migrate', app_name, 'zero',  fake = soft, verbosity = verbosity, database = options['database'])
    printer('Deleting migrations folder', 2)
    try:
      shutil.rmtree(migrations_dir)
    except Exception, ex:
      printer('Failed to delete migrations folder, probably does not exist')
      pass
    printer('Creating new initial migration', 2)
    manage_call('schemamigration', app_name, initial = True, verbosity = verbosity)
    printer('Migrating to new initial', 2)
    manage_call('migrate', app_name, fake = soft, verbosity = verbosity, database = options['database'])
    printer('Done')

class Printer(object):
  def __init__(self, verbosity = 1):
    self.verbosity = int(verbosity)

  def __call__(self, s, verbosity = 1, prefix = '***'):
    if verbosity <= self.verbosity:
      print prefix, s