from django.db import models

# Create your models here.
class StripeCard(models.Model):
  stripe_user = models.CharField(max_length=20)
  exp_month = models.IntegerField()
  exp_year = models.IntegerField()
  card_type = models.CharField(max_length=10, default="Unknown")
  last_four = models.CharField(max_length=4)

  def exp_date(self):
  	return "%s/%s" % (self.exp_month, self.exp_year)