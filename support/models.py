from django.db import models

# Create your models here.

class Email(models.Model):

  subject = models.CharField(max_length=64)
  sender = models.CharField(max_length=32)
  recipients = models.CharField(max_length=512) 
  text = models.TextField()
  html = models.TextField()
  timestamp = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "%s TO %s" % (subject, recipients)

