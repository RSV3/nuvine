from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.

class UserProfile(models.Model):
  user = models.OneToOneField(User)

  accepted_tos = models.BooleanField(default=False)
  age = models.IntegerField(default=0)
  above_21 = models.BooleanField(default=False)

def create_user_profile(sender, instance, created, **kwargs):
  if created:
    UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
