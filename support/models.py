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
  vinely_category2 = models.FloatField(default=1.0)
  vintage = models.CharField(max_length=64, blank=True, null=True)
  varietal = models.CharField(max_length=32, blank=True, null=True)
  region = models.CharField(max_length=64, blank=True, null=True)
  alcohol = models.FloatField(default=0.0)
  residual_sugar = models.FloatField(default=0.0)
  acidity = models.FloatField(default=0.0)
  ph = models.FloatField(default=0.0)
  oak = models.FloatField(default=0.0)
  body = models.FloatField(default=0.0)
  fruit = models.FloatField(default=0.0)
  tannin = models.FloatField(default=0.0)
  supplier = models.CharField(max_length=64, blank=True, null=True)

  sparkling = models.BooleanField(default=False)

  WINE_COLOR = (
    (0, u'Red'),
    (1, u'White'),
    (2, u'Ros\xc3')
  )

  color = models.IntegerField(choices=WINE_COLOR, default=WINE_COLOR[0][0])
  comment = models.CharField(max_length=255, blank=True, null=True)
  price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return "%s [%.1f, %s, %s]" % (self.name, self.vinely_category2, self.get_color_display(), "Sparkling" if self.sparkling else "Regular")


class WineInventory(models.Model):
  wine = models.ForeignKey(Wine)
  on_hand = models.IntegerField(default=0)
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)
