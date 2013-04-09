from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ProLevel(models.Model):

  user = models.ForeignKey(User)

  PRO_LEVEL_CHOICES = (
    (0, "Pro"),
    (1, "Active Pro"),
    (2, "Advanced Pro"),
    (3, "Elite Pro"),
    (4, "Executive Pro"),
  )
  level = models.IntegerField(choices=PRO_LEVEL_CHOICES, default=0)
  updated = models.DateTimeField(auto_now=True)


class ProLevelLog(models.Model):

  user = models.ForeignKey(User)

  level = models.IntegerField(choices=ProLevel.PRO_LEVEL_CHOICES, default=0)
  created = models.DateTimeField(auto_now_add=True)


class WeeklyCompensation(models.Model):
  """
    Calculates weekly compensation

    Need to calculate it from Sunday 1 AM to Sunday 1 AM PST
  """

  pro = models.ForeignKey(User)
  total_personal_sales = models.DecimalField(max_digits=15, decimal_places=2)
  tier_a_personal_sales = models.DecimalField(max_digits=15, decimal_places=2)
  tier_b_personal_sales = models.DecimalField(max_digits=15, decimal_places=2)
  total_earnings = models.DecimalField(max_digits=15, decimal_places=2)
  tier_a_base_earnings = models.DecimalField(max_digits=14, decimal_places=2)
  tier_b_base_earnings = models.DecimalField(max_digits=14, decimal_places=2)
  start_time = models.DateTimeField()
  end_time = models.DateTimeField()

  def __unicode__(self):
    return "%s [total: %.2f, tier_a: %.2f, tier_b: %.2f] earnings:[total: %.2f, tier_a: %.2f, tier_b: %.2f] %s" % (
      self.pro.email, self.total_personal_sales, self.tier_a_personal_sales, self.tier_b_personal_sales,
      self.total_earnings, self.tier_a_base_earnings, self.tier_b_base_earnings, self.start_time)


class MonthlyQualification(models.Model):
  """
    Calculates monthly compensation

    1 AM first of the month to 1 AM PST on the first of the month
  """

  pro = models.ForeignKey(User)
  total_personal_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
  total_sales_1st_line = models.DecimalField(max_digits=15, decimal_places=2, default=0)
  active_pros = models.IntegerField(default=0)
  advanced_pros = models.IntegerField(default=0)
  elite_pros = models.IntegerField(default=0)
  qualification_level = models.IntegerField(choices=ProLevel.PRO_LEVEL_CHOICES, default=0)
  start_time = models.DateTimeField(null=True)
  end_time = models.DateTimeField(null=True)


class MonthlyBonusCompensation(models.Model):
  """
    Calculates the bonus for tier 1 and tier 2 sales

    1 AM first of the month to 1 AM PST on the first of the month
  """

  pro = models.ForeignKey(User)
  qualification_level = models.IntegerField(choices=ProLevel.PRO_LEVEL_CHOICES, default=0)
  total_personal_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
  tier_a_personal_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
  tier_b_personal_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
  total_first_downline_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
  total_second_downline_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
  total_third_downline_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
  tier_a_bonus = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  tier_b_bonus = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  first_line_bonus = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  second_line_bonus = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  third_line_bonus = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  start_time = models.DateTimeField(null=True)
  end_time = models.DateTimeField(null=True)
