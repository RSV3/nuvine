from django.db import models

# Create your models here.

class ContactReason(models.Model):
  reason = models.CharField(max_length=1024)

class ContactRequest(models.Model):

  SEX_CHOICES = (
      (0, 'Female'),
      (1, 'Male'),
      (2, 'Neither'),
  )

  subject = models.ForeignKey(ContactReason)
  first_name = models.CharField(max_length=64)
  last_name = models.CharField(max_length=64, null=True, blank=True)
  sex = models.IntegerField(choices=SEX_CHOICES, default=0)
  email = models.EmailField(verbose_name="E-mail", unique=True)
  message = models.TextField()
  zipcode = models.CharField(max_length=12)
