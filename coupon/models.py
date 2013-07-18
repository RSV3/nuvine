from django.db import models
from main.models import Product
# Create your models here.


class Coupon(models.Model):
  # from main.models import Product

  DURATION_CHOICES = (
      (0, 'One Time'),
      (1, 'Forever'),
      (2, 'Repeating'),
  )
  STRIPE_DURATION_CHOICES = {
      0: 'once',
      1: 'repeating',
      2: 'forever',
  }
  # APPLICATION_CHOICES = (
  #     (0, 'Tasting Kit'),
  #     (1, '3 Bottle VIP'),
  #     (2, '6 Bottles'),
  #     (3, '12 Bottles'),
  # )
  name = models.CharField(max_length=24)
  code = models.CharField(max_length=16, unique=True, verbose_name='Coupon Code')
  active = models.BooleanField(default=True, verbose_name='Enabled')
  duration = models.IntegerField(choices=DURATION_CHOICES, default=0)
  repeat_duration = models.IntegerField(default=0, help_text="If repeating, how long in months")
  amount_off = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  percent_off = models.IntegerField(default=0)
  max_redemptions = models.IntegerField(default=1, verbose_name='Number of Uses', help_text='How many times can it be redeemed')
  redeem_by = models.DateField(verbose_name='Expiration Date')
  applies_to = models.ManyToManyField(Product)
  times_redeemed = models.IntegerField(default=0)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
