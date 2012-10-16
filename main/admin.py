from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from main.models import MyHost, ProSignupLog, EngagementInterest, Party
from main.utils import send_pro_assigned_notification_email, send_host_vinely_party_email


class ProAssignedFilter(SimpleListFilter):

  title = _('pro assigned')

  parameter_name = 'host_assignment'

  def lookups(self, request, model_admin):
    return (
        ('Yes', 'Pro Assigned'),
        ('No', 'No Pro Assigned'),
      )

  def queryset(self, request, queryset):
    pro_assigned = self.value()
    if pro_assigned == 'Yes':
      return queryset.exclude(pro__isnull=True)
    if pro_assigned == 'No':
      return queryset.filter(pro__isnull=True)


class MyHostAdmin(admin.ModelAdmin):
  list_display = ('id', 'pro', 'pro_info', 'pro_account', 'host_info', 'host_zipcode', 'email_entered', 'timestamp')
  raw_id_fields = ['pro', 'host']
  list_filter = (ProAssignedFilter, )
  list_display_links = ('id', )
  list_editable = ('pro', )
  ordering = ['-timestamp']

  def pro_info(self, instance):
    return "%s %s <%s>" % (instance.pro.first_name, instance.pro.last_name, instance.pro.email)

  def host_info(self, instance):
    return "%s %s <%s>" % (instance.host.first_name, instance.host.last_name, instance.host.email)

  def host_zipcode(self, instance):
    return instance.host.get_profile().zipcode

  def pro_account(self, instance):
    acc = instance.pro.vinelyproaccount_set.all()
    return "".join([u.account_number for u in acc])

  def save_model(self, request, obj, form, change):
    if obj.pro and obj.host:
      # new pro was assigned, so send e-mail to the host
      send_pro_assigned_notification_email(request, obj.pro, obj.host)
      send_host_vinely_party_email(request, obj.host, obj.pro)
      messages.info(request, "New pro has been successfully assigned.")
    super(MyHostAdmin, self).save_model(request, obj, form, change)


class ProSignupLogAdmin(admin.ModelAdmin):
  list_display = ['new_pro_info', 'mentor', 'mentor_info', 'mentor_email']
  ordering = ['-timestamp']
  raw_id_fields = ['mentor']
  list_editable = ['mentor']

  def new_pro_info(self, instance):
    return "%s %s <%s>" % (instance.new_pro.first_name, instance.new_pro.last_name, instance.new_pro.email)

  def mentor_info(self, instance):
    if instance:
      return "%s %s <%s>" % (instance.mentor.first_name, instance.mentor.last_name, instance.mentor.email)
    else:
      return "No mentor assigned"


class EngagementInterestAdmin(admin.ModelAdmin):
  list_display = ['user_info', 'engagement_type', 'latest', 'timestamp']
  ordering = ['-timestamp']

  def user_info(self, instance):
    return "%s %s <%s>" % (instance.user.first_name, instance.user.last_name, instance.user.email)


class PartyAdmin(admin.ModelAdmin):
  list_display = ['title', 'event_date', 'host_info', 'description', 'address', 'created']
  raw_id_fields = ['host']
  #list_editable = ['host']
  search_fields = ['title', 'host__first_name', 'host__last_name']
  ordering = ['-event_date']

  def host_info(self, instance):
    return "%s %s <%s>" % (instance.host.first_name, instance.host.last_name, instance.host.email)

admin.site.register(MyHost, MyHostAdmin)
admin.site.register(ProSignupLog, ProSignupLogAdmin)
admin.site.register(EngagementInterest, EngagementInterestAdmin)
admin.site.register(Party, PartyAdmin)
