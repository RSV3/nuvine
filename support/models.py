from django.db import models

# Create your models here.

class Email(models.Model):

  subject = models.CharField(max_length=128)
  sender = models.CharField(max_length=64)
  recipients = models.CharField(max_length=512) 
  text = models.TextField()
  html = models.TextField()
  timestamp = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "%s TO %s" % (self.subject, self.recipients)

  def recipients_list(self):
    return eval(self.recipients)
