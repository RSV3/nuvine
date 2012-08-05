import numpy as np
from personality.models import WinePersonality

def old_calculate_wine_personality(user, wine1, wine2, wine3, wine4, wine5, wine6):
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

def calculate_wine_personality(user, wine1, wine2, wine3, wine4, wine5, wine6):
  """
    Calculate wine personality based on ratings from 6 wines
  """

  wine_personality = 'Complex'
  character = ''

  personality_matrix = np.array([
                                [6, 1, 1, 1, 1, 3, 1, 1],
                                [3, 5, 5, 5, 5, 3, 3, 6],
                                [5, 5, 6, 5, 6, 3, 6, 6],
                                [2, 4, 4, 4, 4, 4, 4, 6],
                                [2, 4, 6, 4, 6, 4, 6, 6],
                                [2, 4, 4, 4, 4, 4, 4, 6],
                                [5, 6, 6, 6, 6, 3, 6, 6],
                                [5, 6, 6, 6, 6, 6, 6, 6]])


  wine_vec = np.array([wine1.overall, wine2.overall, wine3.overall, wine4.overall, wine5.overall, wine6.overall])
  #print wine_vec

  white_vec = np.array([wine1.overall, wine2.overall, wine3.overall])
  red_vec = np.array([wine4.overall, wine5.overall, wine6.overall])

  white = 0
  red = 0
  if np.sum(white_vec >= 3) == 0:
    white = 0
  elif np.sum((white_vec >= 3) == [True, False, False]) == 3:
    white = 1
  elif np.sum((white_vec >= 3) == [True, True, False]) == 3:
    white = 2
  elif np.sum((white_vec >= 3) == [False, True, False]) == 3:
    white = 3
  elif np.sum((white_vec >= 3) == [False, True, True]) == 3:
    white = 4
  elif np.sum((white_vec >= 3) == [False, False, True]) == 3:
    white = 5
  elif np.sum((white_vec >= 3) == [True, False, True]) == 3:
    white = 6
  elif np.sum((white_vec >= 3) == [True, True, True]) == 3:
    white = 7

  if np.sum(red_vec >= 3) == 0:
    red = 0
  elif np.sum((red_vec >= 3) == [True, False, False]) == 3:
    red = 1
  elif np.sum((red_vec >= 3) == [True, True, False]) == 3:
    red = 2
  elif np.sum((red_vec >= 3) == [False, True, False]) == 3:
    red = 3
  elif np.sum((red_vec >= 3) == [False, True, True]) == 3:
    red = 4
  elif np.sum((red_vec >= 3) == [False, False, True]) == 3:
    red = 5
  elif np.sum((red_vec >= 3) == [True, False, True]) == 3:
    red = 6
  elif np.sum((red_vec >= 3) == [True, True, True]) == 3:
    red = 7

  profile = user.get_profile()
  profile.wine_personality = WinePersonality.objects.get(id=personality_matrix[red, white])
  profile.save()

  return profile.wine_personality
