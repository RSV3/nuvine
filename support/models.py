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
  inventory_file = models.FileField(verbose_name="Upload File:", help_text="Select inventory file to upload", upload_to="wine_inventory")
  comment = models.CharField(blank=True, null=True, max_length=128)
  created = models.DateTimeField(auto_now_add=True)


class Wine(models.Model):
  name = models.CharField(max_length=32)
  year = models.IntegerField(default=0)
  sku = models.CharField(max_length=32, blank=True, null=True)
  vinely_category = models.IntegerField(default=1)
  sparkling = models.BooleanField(default=False)

  WINE_COLOR = (
    (0, u'Red'),
    (1, u'White'),
    (2, u'Ros\xc3')
  )

  color = models.IntegerField(choices=WINE_COLOR, default=WINE_COLOR[0][0])
  comment = models.CharField(max_length=255, blank=True, null=True)
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "%s [%d, %s, %s]" % (self.name, self.vinely_category, self.get_color_display(), "Sparkling" if self.sparkling else "Regular")


class WineInventory(models.Model):
  wine = models.ForeignKey(Wine)
  on_hand = models.IntegerField(default=0)
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)
