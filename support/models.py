from django.db import models
from django.conf import settings

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


class InventoryUpload(models.Model):
  inventory_file = models.FileField(upload_to="wine_inventory")
  comment = models.CharField(default=0, max_length=128)
  created = models.DateTimeField(auto_now_add=True)


class Wine(models.Model):
  name = models.CharField(max_length=32)
  year = models.IntegerField(default=0)
  sku = models.CharField(max_length=32, blank=True, null=True)
  vinely_category = models.IntegerField(default=1)
  comment = models.CharField(max_length=255, blank=True, null=True)
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "%s (%s)" % (self.name, self.year)


class WineInventory(models.Model):
  wine = models.ForeignKey(Wine)
  on_hand = models.IntegerField(default=0)
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)
