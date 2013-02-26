from django.db import models
from django.conf import settings

# Create your models here.
from personality.models import Wine


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


class InventoryUpload(models.Model):
  inventory_file = models.FileField(verbose_name="Upload File:", help_text="Select inventory file to upload", upload_to="profiles")
  comment = models.CharField(blank=True, null=True, max_length=128)
  created = models.DateTimeField(auto_now_add=True)


class WineInventory(models.Model):
  wine = models.OneToOneField(Wine)
  on_hand = models.IntegerField(default=0)
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name_plural = u'Wine Inventory'
