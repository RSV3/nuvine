from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.http import HttpRequest
from optparse import make_option

from main.models import Order
from main.utils import send_order_shipped_email

class Command(BaseCommand):

  args = ''
  help = 'Send out test e-mails'

  option_list = BaseCommand.option_list + (
    make_option('-f', '--file',
            type='string',
            dest='filename',
            default=None,
            help='The excel file name of master database.'),
    )

  def handle(self, *args, **options):
    order = Order.objects.all().order_by("-order_date")[0]
    user = User.objects.get(email="jayme@vinely.com")
    order.receiver = user
    order.ordered_by = user
    request = HttpRequest()
    request.META['SERVER_NAME'] = "www.vinely.com"
    request.META['SERVER_PORT'] = 80
    request.user = user

    send_order_shipped_email(request, order)
