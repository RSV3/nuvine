from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from personality.models import WineRatingData
from personality.utils import calculate_wine_personality

import logging

log = logging.getLogger(__name__)


class Command(BaseCommand):
  args = ''
  help = 'Users wine personality are updated'

  def handle(self, *args, **options):

    for u in User.objects.all():
      if WineRatingData.objects.filter(user=u).count() >= 6:
        log.info("Original Personality: {email} - {personality}".format(email=u.email,
                                            personality=u.get_profile().wine_personality))
        wine1 = WineRatingData.objects.filter(user=u, wine__id=1)[0]
        wine2 = WineRatingData.objects.filter(user=u, wine__id=2)[0]
        wine3 = WineRatingData.objects.filter(user=u, wine__id=3)[0]
        wine4 = WineRatingData.objects.filter(user=u, wine__id=4)[0]
        wine5 = WineRatingData.objects.filter(user=u, wine__id=5)[0]
        wine6 = WineRatingData.objects.filter(user=u, wine__id=6)[0]
        calculate_wine_personality(u, wine1, wine2, wine3, wine4, wine5, wine6)
        log.info("New Personality: {email} - {personality}".format(email=u.email,
                                            personality=u.get_profile().wine_personality))
