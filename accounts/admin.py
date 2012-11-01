from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.admin import SimpleListFilter
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from accounts.models import UserProfile, VinelyProAccount, Address
from accounts.utils import send_pro_approved_email
from main.utils import send_mentor_assigned_notification_email, send_mentee_assigned_notification_email, generate_pro_account_number

from main.models import MyHost

from emailusernames.admin import EmailUserAdmin

def approve_pro(modeladmin, request, queryset):
  for obj in queryset:
    user = obj.user
    user.groups.clear()
    pro_group = Group.objects.get(name="Vinely Pro")
    user.groups.add(pro_group)
    if not VinelyProAccount.objects.filter(users__in = [user]).exists():
      pro_account_number = generate_pro_account_number()
      account, created = VinelyProAccount.objects.get_or_create(account_number = pro_account_number)
      account.users.add(user)

    # TODO: need to send out e-mail to the user
    send_pro_approved_email(request, user)

approve_pro.short_description = "Approve selected users as Vinely Pro"

def remove_pro_privileges(modeladmin, request, queryset):
  for obj in queryset:
    user = obj.user
    user.groups.clear()
    pro_group = Group.objects.get(name="Pending Vinely Pro")
    user.groups.add(pro_group)

remove_pro_privileges.short_description = "Remove Vinely Pro permissions for selected users"

def change_to_host(modeladmin, request, queryset):
  for obj in queryset:
    user = obj.user
    user.groups.clear()
    host_group = Group.objects.get(name="Vinely Host")
    user.groups.add(host_group)
    try:
      MyHost.objects.get(host=user)
    except MyHost.DoesNotExist:
      MyHost.objects.create(pro=None, host=user)

change_to_host.short_description = "Change user to a host"

def change_to_taster(modeladmin, request, queryset):
  for obj in queryset:
    user = obj.user
    user.groups.clear()
    taster_group = Group.objects.get(name="Vinely Taster")
    user.groups.add(taster_group)
    for my_host in MyHost.objects.filter(host=user):
      my_host.delete()

change_to_taster.short_description = "Change user to a taster"

class MentorAssignedFilter(SimpleListFilter):

  title = _('mentor assigned')

  parameter_name = 'mentor_assigned'

  def lookups(self, request, model_admin):
    return (
        ( 'Yes', 'Mentor Assigned'),
        ( 'No', 'No Mentor Assigned'),
      )

  def queryset(self, request, queryset):
    mentor_assigned = self.value()
    if mentor_assigned == 'Yes':
      return queryset.exclude(mentor__isnull=True)
    if mentor_assigned == 'No':
      return queryset.filter(mentor__isnull=True)

class VinelyUserProfileAdmin(admin.ModelAdmin):

  list_display = ('email', 'full_name', 'user_image', 'dob', 'phone', 'zipcode', 'news_optin_flag', 'wine_personality', 'user_type', 'mentor_email', 'pro_number')
  list_filter = ('user__groups', MentorAssignedFilter)
  list_editable = ('wine_personality', )
  raw_id_fields = ('user', 'mentor')
  model = UserProfile
  actions = [approve_pro, remove_pro_privileges, change_to_host, change_to_taster]
  search_fields = ['user__first_name', 'user__last_name']

  def user_image(self, instance):
    if instance.image:
      return '<img src="%s%s" height="75"/>' % (settings.MEDIA_URL, instance.image)
    else:
      return 'No Image'
  user_image.allow_tags = True

  def news_optin_flag(self, instance):
    return instance.news_optin
  news_optin_flag.short_description = 'Newsletter Optin'
  news_optin_flag.boolean = True

  def email(self, instance):
    return instance.user.email

  def mentor_email(self, instance):
    return instance.mentor.email

  def full_name(self, instance):
    return "%s %s" % (instance.user.first_name, instance.user.last_name)

  def user_type(self, instance):
    try:
      group = instance.user.groups.all()[0]
      return group.name
    except IndexError:
      return "Unassigned"

  def pro_number(self, instance):
    return "".join([acc.account_number for acc in VinelyProAccount.objects.filter(users=instance.user)])

  def save_model(self, request, obj, form, change):
    old_profile = UserProfile.objects.get(id=obj.pk)
    if obj.mentor != old_profile.mentor:
      # new pro was assigned, so send e-mail to the host
      send_mentor_assigned_notification_email(request, obj.user, obj.mentor)
      send_mentee_assigned_notification_email(request, obj.mentor, obj.user)
      messages.info(request, "New mentor has been successfully assigned.")
    super(VinelyUserProfileAdmin, self).save_model(request, obj, form, change)

admin.site.register(UserProfile, VinelyUserProfileAdmin)
admin.site.unregister(User)

class VinelyUserAdmin(EmailUserAdmin):

  list_display = ('email', 'first_name', 'last_name', 'user_type', 'zipcode', 'pro_number')
  list_filter = ('groups', 'is_active')

  def user_type(self, instance):
    if instance.groups.all().count() > 0:
      group = instance.groups.all()[0]
      return group.name
    else:
      return "No group"

  def zipcode(self, instance):
    zipcode_str = instance.get_profile().zipcode
    return zipcode_str

  def pro_number(self, instance):
    return "".join([acc.account_number for acc in VinelyProAccount.objects.filter(users=instance)])

class AddressAdmin(admin.ModelAdmin):
  pass

admin.site.register(User, VinelyUserAdmin)
admin.site.register(Address, AddressAdmin)
