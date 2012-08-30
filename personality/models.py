from django.db import models
from django.contrib.auth.models import User 


# Create your models here.

class Wine(models.Model):
  name = models.CharField(max_length=128)
  year = models.IntegerField(default=0)
  sip_bits = models.TextField()
  number = models.IntegerField(default=0)
  active = models.BooleanField(default=False)
  price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
  # the date this wine was added
  added = models.DateField(auto_now_add=True)
  # the date this wine is no longer used for tasting
  deactivated = models.DateField(null=True, blank=True)

  def deactivate(self):
    self.active = False
    self.deactivated = date.today()
    self.save()

  def activate(self):
    self.active = True
    self.save()

  def __unicode__(self):
    return "%s: %s"%(self.number, self.name)

class WineRatingData(models.Model):

  LIKENESS_CHOICES = (
      (0, 'Not Answered'),
      (1, 'Hate'),
      (2, 'Dislike'),
      (3, 'Neutral'),
      (4, 'Like'),
      (5, 'Love'),
  )

  DNL_CHOICES = (
    (0, 'Not Answered'),
    (1, 'Dislike'),
    (2, 'Neutral'),
    (3, 'Like'),
  )

  SWEET_CHOICES = (
    (0, 'Not Answered'),
    (1, 'Very Tart'),
    (2, 'Tart'),
    (3, 'Neutral'),
    (4, 'Sweet'),
    (5, 'Very Sweet'),
  )
  
  WEIGHT_CHOICES = (
    (0, 'Not Answered'),
    (1, 'Very Light'),
    (2, 'Light'),
    (3, 'Medium'),
    (4, 'Heavy'),
    (5, 'Very Heavy'),
  )

  TEXTURE_CHOICES = (
    (0, 'Not Answered'),
    (1, 'Very Silky'),
    (2, 'Silky'),
    (3, 'Neutral'),
    (4, 'Furry'),
    (5, 'Very Furry'),
  )

  SIZZLE_CHOICES = (
    (0, 'Not Answered'),
    (1, 'None'),
    (2, 'Somewhat'),
    (3, 'Tingle'),
    (4, 'Burn'),
    (5, 'Hot')
  )

  user = models.ForeignKey(User)
  wine = models.ForeignKey(Wine)
  overall = models.IntegerField(choices=LIKENESS_CHOICES, default=LIKENESS_CHOICES[0][0])
  dnl = models.IntegerField(choices=DNL_CHOICES, default=DNL_CHOICES[0][0])
  sweet = models.IntegerField(choices=SWEET_CHOICES, default=SWEET_CHOICES[0][0]) 
  sweet_dnl = models.IntegerField(choices=DNL_CHOICES, default=DNL_CHOICES[0][0])
  weight = models.IntegerField(choices=WEIGHT_CHOICES, default=WEIGHT_CHOICES[0][0]) 
  weight_dnl = models.IntegerField(choices=DNL_CHOICES, default=DNL_CHOICES[0][0])
  texture = models.IntegerField(choices=TEXTURE_CHOICES, default=TEXTURE_CHOICES[0][0]) 
  texture_dnl = models.IntegerField(choices=DNL_CHOICES, default=DNL_CHOICES[0][0])
  sizzle = models.IntegerField(choices=SIZZLE_CHOICES, default=SIZZLE_CHOICES[0][0]) 
  sizzle_dnl = models.IntegerField(choices=DNL_CHOICES, default=DNL_CHOICES[0][0])
  timestamp = models.DateTimeField(auto_now_add=True)

class WinePersonality(models.Model):
  """
    Existing wine personalities
  """
  name = models.CharField(max_length=32)
  headline = models.CharField(max_length=64)
  suffix = models.CharField(max_length=16)
  description = models.TextField()

  def __unicode__(self):
    return self.name

class SurveyWine(models.Model):

  name = models.CharField(max_length=32)

  COLOR_CHOICES = (
    (0, 'Red'),
    (1, 'White'),
    (2, 'Other')
  )
  color = models.IntegerField(choices=COLOR_CHOICES, default=COLOR_CHOICES[0][0])

  def __unicode__(self):
    return self.name

class GeneralTaste(models.Model):
  """
    General taste questionnaire
  """

  user = models.ForeignKey(User)

  # question 1
  DRINK_REGULAR_CHOICES = (
      (1, 'Coffee.'),
      (2, 'Tea.'),
      (3, 'Neither.')
  )
  drink_regularly = models.IntegerField(choices=DRINK_REGULAR_CHOICES, default=0, verbose_name='What do you drink most regularly?')

  # question 2
  COFFEE_CHOICES = (
      (1, 'Bold.'),
      (2, 'Medium.'),
      (3, 'Mild.')
  )
  coffee_type = models.IntegerField(choices=COFFEE_CHOICES, default=0, verbose_name='What type of [coffee/tea] do you prefer?', blank=True, null=True)

  # question 3
  COFFEE_TAKE_CHOICES = (
      (1, 'Plain.'),
      (2, 'With cream.'),
      (3, 'With sugar.'),
      (4, 'With cream and sugar.'),
  )
  coffee_take = models.IntegerField(choices=COFFEE_TAKE_CHOICES, default=0, verbose_name='How do you typically take your [coffee/tea]?', blank=True, null=True)

  # question 4
  SALTY_FOOD_CHOICES = (
      (1, 'The more salty, the better.'),
      (2, 'I enjoy the taste, but in moderation.'),
      (3, 'If it\'s not there, I don\'t even notice.'),
      (4, 'Don\'t care for it.'),
      (5, 'Hate salt altogether.'),
  )
  salty_food = models.IntegerField(choices=SALTY_FOOD_CHOICES, default=0, verbose_name='Do you enjoy salty food/snacks?', blank=True, null=True)

  # question 5
  CITRUS_CHOICES = (
      (1, 'I love lemons and limes on their own.'),
      (2, 'I prefer it with a touch of sweetness, like grapefruit juice.'),
      (3, 'On the sweeter side.  Like orange juice.'),
      (4, 'As a soda flavor.'),
      (5, 'I do not enjoy citrus, whatsoever.'),
  )
  citrus = models.IntegerField(choices=CITRUS_CHOICES, default=0, verbose_name='How do you like your citrus?')

  # question 6
  EARTHY_CHOICES = (
      (1, 'Love, love, love\'em.'),
      (2, 'I\'ll take them as an addition to a dish.'),
      (3, 'A touch will do, bu that\'s it.'),
      (4, 'Not really a fan.'),
      (5, 'I\'d rather walk on them than eat them.'),
  )
  earthy = models.IntegerField(choices=EARTHY_CHOICES, default=0, verbose_name='Tell us your feelings on earthy FLAVORS like mushrooms and truffles.')

  # question 7
  BERRIES_CHOICES = (
      (1, 'I enjoy them all by themselves.'),
      (2, 'I like them in a dessert.'),
      (3, 'They\'re great.  But I\'d rather eat them as a jelly or jam.'),
      (4, 'They\'re OK.'),
      (5, 'Berries? Ick.')
  )
  berries = models.IntegerField(choices=BERRIES_CHOICES, default=0, verbose_name='How do you feel about berries?')

  # question 8
  ARTIFICIAL_CHOICES = (
      (1, 'Every day, all the time.'),
      (2, 'On occasion.'),
      (3, 'I use them only if my food or drink really needs sweetening.'),
      (4, 'Rarely.'),
      (5, 'No way.')
  )
  artificial = models.IntegerField(choices=ARTIFICIAL_CHOICES, default=0, verbose_name='Do you use artificial sweeteners or consume products with sweeteners in them (i.e. diet soda)?')

  # question 9
  NEW_FLAVORS_CHOICES = (
      (1, 'All the time!'),
      (2, 'Often.'),
      (3, 'Sometimes.'),
      (4, 'Rarely.'),
      (5, 'Never.')
  )
  new_flavors = models.IntegerField(choices=NEW_FLAVORS_CHOICES, default=0, verbose_name='How often do you try out new foods and flavors?')

class WineTaste(models.Model):

  user = models.ForeignKey(User)

  # question 1
  TYPICALLY_DRINK_CHOICES = (
      (1, 'Both red and white wine.'),
      (2, 'Reds only.'),
      (3, 'Whites only.')
  )
  typically_drink = models.IntegerField(choices=TYPICALLY_DRINK_CHOICES, default=0, verbose_name='Do you typically drink: (select one):')

  # question 2
  RED_BODY_CHOICES = (
    (1, 'Light-Medium body'),
    (2, 'Medium-Full body'),
    (3, 'No Clue/It Depends')
  )
  red_body = models.IntegerField(choices=RED_BODY_CHOICES, default=0, verbose_name='Body', blank=True, null=True)

  RED_SWEETNESS_CHOICES = (
    (1, 'Sweet'),
    (2, 'Dry'),
    (3, 'No Clue/It Depends')
  ) 
  red_sweetness = models.IntegerField(choices=RED_SWEETNESS_CHOICES, default=0, verbose_name='Sweetness', blank=True, null=True)

  RED_ACIDITY_CHOICES = (
    (1, 'Smooth'),
    (2, 'Tingly'),
    (3, 'No Clue/It Depends')
  )
  red_acidity = models.IntegerField(choices=RED_ACIDITY_CHOICES, default=0, verbose_name='Acidity', blank=True, null=True)

  RED_COLOR_CHOICES = (
    (1, 'Light'),
    (2, 'Dark'),
    (3, 'No Clue/It Depends')
  )
  red_color = models.IntegerField(choices=RED_COLOR_CHOICES, default=0, verbose_name='Color', blank=True, null=True)

  # question 3
  red_wines_often = models.ManyToManyField(SurveyWine, verbose_name='What RED wine(s) do you currently drink most often? (select up to 2)', related_name='survey_red_favorites')
  red_wines_other = models.CharField(max_length=32, null=True, blank=True, verbose_name="Other (please specify):")
  
  # question 4
  red_wine_dislike = models.ForeignKey(SurveyWine, verbose_name='What RED wine, if any, do you particularly DISLIKE?', null=True, blank=True, related_name='survey_red_dislike') 
  red_wine_dislike_other = models.CharField(max_length=32, null=True, blank=True, verbose_name="Other (please specify):")
  
  # question 5
  WHITE_OAK_CHOICES = (
    (1, 'Oaky'),
    (2, 'Not Oaky'),
    (3, 'No Clue/It Depends'),
  )
  white_oak = models.IntegerField(choices=WHITE_OAK_CHOICES, default=0, verbose_name='Oak:', blank=True, null=True)

  WHITE_SWEETNESS_CHOICES = (
    (1, 'Sweet'),
    (2, 'Dry'),
    (3, 'No Clue/It Depends'),
  )
  white_sweetness = models.IntegerField(choices=WHITE_SWEETNESS_CHOICES, default=0, verbose_name='Sweetness:', blank=True, null=True)

  WHITE_ACIDITY_CHOICES = (
    (1, 'Smooth'),
    (2, 'Tingly'),
    (3, 'No Clue/It Depends'),
  )
  white_acidity = models.IntegerField(choices=WHITE_ACIDITY_CHOICES, default=0, verbose_name='White:', blank=True, null=True)

  WHITE_COLOR_CHOICES = (
    (1, 'Light'),
    (2, 'Dark'),
    (3, 'No Clue/It Depends')
  )
  white_color = models.IntegerField(choices=WHITE_COLOR_CHOICES, default=0, verbose_name='Color:', blank=True, null=True)

  # question 6
  white_wines_often = models.ManyToManyField(SurveyWine, verbose_name='What WHITE wine(s) do you currently drink most often? (select up to 2)', related_name='survey_white_favorites')
  white_wines_other = models.CharField(max_length=32, null=True, blank=True, verbose_name="Specify other wine:")

  # question 7
  white_wine_dislike = models.ForeignKey(SurveyWine, verbose_name='What WHITE wine, if any, do you particularly DISLIKE?', null=True, blank=True, related_name='survey_white_dislike')
  white_wine_dislike_other = models.CharField(max_length=32, null=True, blank=True, verbose_name="Specify other wine:")

  # question 8
  other_wines = models.ManyToManyField(SurveyWine, verbose_name='Do you drink (select all that apply):', related_name='other_likes')
