from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from pro.models import ProLevel, WeeklyCompensation, MonthlyQualification, MonthlyBonusCompensation


class WeeklyCompensationAdmin(admin.ModelAdmin):
  list_display = ['pro', 'total_personal_sales', 'tier_a_personal_sales', 'tier_b_personal_sales',
                  'total_earnings', 'tier_a_base_earnings', 'tier_b_base_earnings',
                  'start_time', 'end_time']
  list_filter = (
      ('start_time', DateFieldListFilter),
    )


class MonthlyQualificationAdmin(admin.ModelAdmin):
  """
    Use following query in order to filter by date
    - url?start_time__gte=2013-02-01&end_time__lte=2013-03-01
  """
  list_display = ['pro', 'total_personal_sales', 'total_sales_1st_line', 'active_pros', 'advanced_pros', 'elite_pros',
              'qualification_level', 'start_time', 'end_time']
  list_filter = (
      ('start_time', DateFieldListFilter),
    )


class MonthlyBonusCompensationAdmin(admin.ModelAdmin):
  list_display = ['pro', 'qualification_level', 'total_personal_sales', 'tier_a_personal_sales', 'tier_b_personal_sales',
                  'total_first_downline_sales', 'total_second_downline_sales', 'total_third_downline_sales',
                  'tier_a_bonus', 'tier_b_bonus', 'first_line_bonus', 'second_line_bonus', 'third_line_bonus',
                  'start_time', 'end_time']
  list_filter = (
      ('start_time', DateFieldListFilter),
    )

admin.site.register(WeeklyCompensation, WeeklyCompensationAdmin)
admin.site.register(MonthlyQualification, MonthlyQualificationAdmin)
admin.site.register(MonthlyBonusCompensation, MonthlyBonusCompensationAdmin)
