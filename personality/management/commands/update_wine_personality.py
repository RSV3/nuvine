from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from personality.models import WineRatingData
from personality.utils import calculate_wine_personality

import numpy as np
import logging

log = logging.getLogger(__name__)


class Command(BaseCommand):
  args = ''
  help = 'Users wine personality are updated'

  def handle(self, *args, **options):

    for u in User.objects.all():
      if WineRatingData.objects.filter(user=u).count() >= 6:
        log.info("Original Personality:\t{email} - {personality}".format(email=u.email,
                                            personality=u.get_profile().wine_personality))
        wine1 = WineRatingData.objects.filter(user=u, wine__id=1)[0]
        wine2 = WineRatingData.objects.filter(user=u, wine__id=2)[0]
        wine3 = WineRatingData.objects.filter(user=u, wine__id=3)[0]
        wine4 = WineRatingData.objects.filter(user=u, wine__id=4)[0]
        wine5 = WineRatingData.objects.filter(user=u, wine__id=5)[0]
        wine6 = WineRatingData.objects.filter(user=u, wine__id=6)[0]
        if np.sum(np.array([wine1.overall, wine2.overall, wine3.overall, wine4.overall, wine5.overall, wine6.overall]) > 0) == 6:
          calculate_wine_personality(u, wine1, wine2, wine3, wine4, wine5, wine6)
          log.info("New Personality:\t\t{email} - {personality}".format(email=u.email,
                                              personality=u.get_profile().wine_personality))
        else:
          log.info("New Personality:\t\t{email} - Mystery".format(email=u.email))

