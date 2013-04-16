# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

from pro.models import ProLevel, WeeklyCompensation, MonthlyQualification, MonthlyBonusCompensation


def build_downline(pro, pro_comp, downline_level=0):
  """
    Used to map down to third downline
  """

  if downline_level > 2:
    return

  try:
    pro.get_profile()
  except UserProfile.DoesNotExist:
    UserProfile.objects.create(user=pro)
    print "New user profile created for %d, %s" % (pro.id, pro.email)

  if pro.get_profile().is_pro() or pro.get_profile().is_pending_pro():

    downline_pros = []
    for mentee_profile in pro.mentees.all():
      if mentee_profile.user.id != pro.id and (mentee_profile.is_pro() or mentee_profile.is_pending_pro()):
        downline_pros.append(mentee_profile.user)

    pro_comp[pro.id] = {
      'pro': pro,
      'downline_level': downline_level,
      'total_sales': 0,
      'tier_a_sales': 0,
      'tier_b_sales': 0,
      'upline': pro.get_profile().mentor,
      'downline': downline_pros,
      'traversed': False,
      'qualified': False,
      'level': ProLevel.PRO_LEVEL_CHOICES[0][0]
    }

    for downline in downline_pros:
      build_downline(downline, pro_comp, downline_level=downline_level+1)


@login_required
def pro_home(request):
  data = {}

  u = request.user

  pro_comp = {}

  build_downline(u, pro_comp)

  # show weekly compensation if this week, up to last month
  data["weekly_comps"] = WeeklyCompensation.objects.filter(pro=u).order_by('-start_time')

  # show last months and past few months commissions/bonus
  data["monthly_comps"] = MonthlyBonusCompensation.objects.filter(pro=u).order_by('-start_time')

  # show past qualifying level for few months
  data["monthly_quals"] = MonthlyQualification.objects.filter(pro=u).order_by('-start_time')

  # show downlines and upline
  data["mentor_pro"] = u.get_profile().mentor
  data["downline"] = [mentee for mentee in u.mentees.all()]

  # show the stats of downline

  return render(request, 'pro/home.html', data)


@staff_member_required
def pro_stats(request):
  """
    View all the stats of pros
  """
  data = {}

  # show all pro network
  pro_comp = {}
  for pro in User.objects.all():
    try:
      pro.get_profile()
    except UserProfile.DoesNotExist:
      UserProfile.objects.create(user=pro)
      print "New user profile created for %d, %s" % (pro.id, pro.email)

    if pro.get_profile().is_pro() or pro.get_profile().is_pending_pro():
      downline_pros = []
      for mentee_profile in pro.mentees.all():
        if mentee_profile.user.id != pro.id and (mentee_profile.is_pro() or mentee_profile.is_pending_pro()):
          downline_pros.append(mentee_profile.user)

      # create new pro comp record
      pro_comp[pro.id] = {
        'pro': pro,
        'total_sales': 0,
        'tier_a_sales': 0,
        'tier_b_sales': 0,
        'upline': pro.get_profile().mentor,
        'downline': downline_pros,
        'traversed': False,
        'qualified': False,
        'level': ProLevel.PRO_LEVEL_CHOICES[0][0]
      }

  # show top pros by week and month
  data["weekly_comps"] = WeeklyCompensation.objects.all().order_by('-start_time')

  # show bottom pros by week and month
  data["monthly_comps"] = MonthlyBonusCompensation.objects.all().order_by('-start_time')

  # show the number of different pro levels currently
  data["monthly_quals"] = MonthlyQualification.objects.all().order_by('-start_time')

  return render(request, 'pro/stats.html', data)

