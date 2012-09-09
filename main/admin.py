from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from main.models import MyHost
from main.utils import send_pro_assigned_notification_email

class ProAssignedFilter(SimpleListFilter):

  title = _('pro assigned')

  parameter_name = 'host_assignment'

  def lookups(self, request, model_admin):
    return (
        ( 'Yes', 'Pro Assigned'),
        ( 'No', 'No Pro Assigned'),
      )

  def queryset(self, request, queryset):
    pro_assigned = self.value()
    if pro_assigned == 'Yes':
      return queryset.exclude(pro__isnull=True)
    if pro_assigned == 'No':
      return queryset.filter(pro__isnull=True)

class MyHostAdmin(admin.ModelAdmin):
  list_display = ('id', 'pro', 'pro_info', 'host_info')
  raw_id_fields = ['pro', 'host']
  list_filter = (ProAssignedFilter, )
  list_display_links = ('id', )
  list_editable = ('pro', )

  def pro_info(self, instance):
    return "%s %s <%s>" % (instance.pro.first_name, instance.pro.last_name, instance.pro.email)

  def host_info(self, instance):
    return "%s %s <%s>" % (instance.host.first_name, instance.host.last_name, instance.host.email)

  def save_model(self, request, obj, form, change):
    if obj.pro and obj.host:
      # new pro was assigned, so send e-mail to the host
      send_pro_assigned_notification_email(request, obj.pro, obj.host)
      messages.info(request, "New pro has been successfully assigned.")
    super(MyHostAdmin, self).save_model(request, obj, form, change)

admin.site.register(MyHost, MyHostAdmin)