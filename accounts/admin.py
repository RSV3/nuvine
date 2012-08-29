from django.contrib import admin
from accounts.models import UserProfile
from django.contrib.auth.models import Group


def approve_pro(modeladmin, request, queryset):
  for obj in queryset:
    user = obj.user
    user.groups.clear()
    pro_group = Group.objects.get(name="Vinely Pro")
    user.groups.add(pro_group)
    # TODO: need to send out e-mail to the user

approve_pro.short_description = "Approve selected users as Vinely Pro"

def defer_pro_privileges(modeladmin, request, queryset):
  for obj in queryset:
    user = obj.user
    user.groups.clear()
    pro_group = Group.objects.get(name="Pending Vinely Pro")
    user.groups.add(pro_group)

defer_pro_privileges.short_description = "Defer selected users Vinely Pro permissions"

class VinelyUserProfileAdmin(admin.ModelAdmin):

  list_display = ('email', 'full_name', 'image', 'dob', 'phone', 'zipcode', 'news_optin_flag', 'wine_personality', 'is_pro')
  list_filter = ('user__groups',)
  list_editable = ('wine_personality', )
  raw_id_fields = ('user', )
  model = UserProfile
  actions = [approve_pro, defer_pro_privileges]
  
  def news_optin_flag(self, instance):
    return instance.news_optin
  news_optin_flag.short_description = 'Newsletter Optin'
  news_optin_flag.boolean = True

  def email(self, instance):
    return instance.user.email

  def full_name(self, instance):
    return "%s %s" % (instance.user.first_name, instance.user.last_name)

  def groups(self, instance):
    return instance.user.groups.all()

  def is_pro(self, instance):
    pro = Group.objects.get(name="Vinely Pro")
    return pro in instance.user.groups.all()


admin.site.register(UserProfile, VinelyUserProfileAdmin)

# need to create a place where Elizabeth can see all the Vinely Pro's
# and need to be able to approve

# Done: need to assign to pro_pending

# Done: pro_pending cannot create parties

# then have a drop down to assign as pro
# trigger an e-mail that you have been approved

