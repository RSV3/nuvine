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
      (1, 'Hated'),
      (2, 'Disliked'),
      (3, 'Neutral'),
      (4, 'Liked'),
      (5, 'Loved'),
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
  description = models.TextField()

  def __unicode__(self):
    return self.name

