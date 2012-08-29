from django.contrib import admin
from accounts.models import UserProfile
from django.contrib.auth.models import Group


class VinelyProApplicants(admin.ModelAdmin):

  list_display = ('email', 'full_name', 'image', 'dob', 'phone', 'news_optin', 'wine_personality', 'is_pro')
  list_filter = ('user__groups',)
  raw_id_fields = ('user', )
  model = UserProfile

  #news_option.short_description = 'Newsletter Optin'

  def email(self, instance):
    return instance.user.email

  def full_name(self, instance):
    return "%s %s" % (instance.user.first_name, instance.user.last_name)

  def groups(self, instance):
    return instance.user.groups.all()

  def is_pro(self, instance):
    pro = Group.objects.get(name="Vinely Pro")
    return pro in instance.user.groups.all()

admin.site.register(UserProfile, VinelyProApplicants)

# need to create a place where Elizabeth can see all the Vinely Pro's
# and need to be able to approve

# Done: need to assign to pro_pending

# Done: pro_pending cannot create parties

# then have a drop down to assign as pro
# trigger an e-mail that you have been approved

