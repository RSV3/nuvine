import numpy as np
from personality.models import WinePersonality

def calculate_wine_personality(user, wine1, wine2, wine3, wine4, wine5, wine6):
  """
    Calculate wine personality based on ratings from 6 wines
  """

  """ 

  6 Categories:

  -> Easy Going
    -> 6 or above on 1 & 2

  -> Whimsical
    -> 6 or above on 3 & 4
    
  -> Exuberant
    -> 6 or above on 4 & 5

  -> Moxie
    -> 6 or above on 5 & 6

  -> Sensational
  - > 6 or above on 5 & 6 & 1

  -> Serendipitous
    -> 6 or above on 5 of 6 wines

  """

  wine_personality = 'Complex'
  character = ''

  wine_vec = np.array([wine1.overall, wine2.overall, wine3.overall, wine4.overall, wine5.overall, wine6.overall])
  #print wine_vec

  if wine1.overall >= 3 and wine2.overall >= 3:
    character += 'Easy Going - '
    wine_personality = 'Easy Going'
  if wine3.overall >= 3 and wine4.overall >= 3:
    character += 'Whimsical - '
    wine_personality = 'Whimsical'
  if wine4.overall >= 3 and wine5.overall >= 3:
    character += 'Exuberant - '
    wine_personality = 'Exuberant'
  if wine5.overall >= 3 and wine6.overall >= 3:
    character += 'Moxie - '
    wine_personality = 'Moxie'
  if wine1.overall >= 3 and wine5.overall >= 3 and wine6.overall >= 3:  
    character += 'Sensational - '
    wine_personality = 'Sensational'
  if np.sum(wine_vec >= 3) >= 5:
    character += 'Serendipitous'
    wine_personality = 'Serendipitous'
  
  profile = user.get_profile()
  profile.wine_personality = WinePersonality.objects.get(name=wine_personality)
  profile.save()

  return profile.wine_personality
