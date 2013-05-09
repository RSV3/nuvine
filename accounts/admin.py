from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.admin import SimpleListFilter
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from accounts.models import UserProfile, VinelyProAccount, Address, SubscriptionInfo, Zipcode
from accounts.utils import send_pro_approved_email, reassign_pro
from main.utils import send_mentor_assigned_notification_email, send_mentee_assigned_notification_email, \
                        generate_pro_account_number, my_pro, send_pro_assigned_notification_email, send_host_vinely_party_email

from main.models import MyHost, Cart

from emailusernames.admin import EmailUserAdmin
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

import logging
log = logging.getLogger(__name__)


def approve_pro(modeladmin, request, queryset):
  for obj in queryset:

    user = obj.user
    obj.role = UserProfile.ROLE_CHOICES[1][0]
    obj.save()
    if not VinelyProAccount.objects.filter(users__in=[user]).exists():
      pro_account_number = generate_pro_account_number()
      account, created = VinelyProAccount.objects.get_or_create(account_number=pro_account_number)
      account.users.add(user)

    # TODO: need to send out e-mail to the user
    send_pro_approved_email(request, user)

approve_pro.short_description = "Approve selected users as Vinely Pro"


def remove_pro_privileges(modeladmin, request, queryset):
  for obj in queryset:
    obj.role = UserProfile.ROLE_CHOICES[5][0]
    obj.save()

remove_pro_privileges.short_description = "Remove Vinely Pro permissions for selected users"


def change_to_host(modeladmin, request, queryset):
  for obj in queryset:
    user = obj.user
    obj.role = UserProfile.ROLE_CHOICES[2][0]
    obj.save()
    try:
      MyHost.objects.get(host=user)
    except MyHost.DoesNotExist:
      MyHost.objects.create(pro=None, host=user)

change_to_host.short_description = "Change user to a host"


def change_to_taster(modeladmin, request, queryset):
  for obj in queryset:
    user = obj.user

    obj.role = UserProfile.ROLE_CHOICES[3][0]
    obj.save()

    for my_host in MyHost.objects.filter(host=user):
      my_host.delete()

change_to_taster.short_description = "Change user to a taster"


def cancel_subscription(modeladmin, request, queryset):
  users = []
  for obj in queryset:
    if isinstance(modeladmin, SubscriptionAdmin):
      obj.user.userprofile.cancel_subscription()
    else:  # instanceof userprofile
      obj.cancel_subscription()
    users.append(obj.user.email)
  messages.warning(request, "Subscription has been cancelled for %s" % ", ".join(users))

cancel_subscription.short_description = "Cancel subscription"


def leave_vinely(modeladmin, request, queryset):
  for obj in queryset:
    reassign_pro(obj.user)
  messages.success(request, "The selected Pro(s) were deactivated and their followers reassigned.")


class MentorAssignedFilter(SimpleListFilter):

  title = _('mentor assigned')

  parameter_name = 'mentor_assigned'

  def lookups(self, request, model_admin):
    return (
        ('Yes', 'Mentor Assigned'),
        ('No', 'No Mentor Assigned'),
    )

  def queryset(self, request, queryset):
    mentor_assigned = self.value()

    # select only pro's
    pros = [prof.id for prof in UserProfile.objects.all() if prof.is_pro()]

    if mentor_assigned == 'Yes':
      return queryset.filter(id__in=pros).exclude(mentor__isnull=True)
    if mentor_assigned == 'No':
      return queryset.filter(id__in=pros, mentor__isnull=True)


class ProAssignedFilter(SimpleListFilter):

  title = _('pro assigned')

  parameter_name = 'pro_assigned'

  def lookups(self, request, model_admin):
    return (
        ('Yes', 'Pro Assigned'),
        ('No', 'No Pro Assigned'),
    )

  def queryset(self, request, queryset):
    pro_assigned = self.value()

    non_pros = [prof.id for prof in UserProfile.objects.all() if prof.is_host() or prof.is_taster()]

    if pro_assigned == 'Yes':
      return queryset.filter(id__in=non_pros).exclude(current_pro__isnull=True)
    if pro_assigned == 'No':
      return queryset.filter(id__in=non_pros, current_pro__isnull=True)

from django import forms
from django.forms.util import ErrorList


class VinelyUserProfileForm(forms.ModelForm):
  class Meta:
    model = UserProfile

  def clean(self):
    cleaned_data = super(VinelyUserProfileForm, self).clean()
    if self.instance.is_pro():
      # can only set mentor
      if cleaned_data['current_pro']:
        self._errors["current_pro"] = ErrorList([u'You cannot set a "current pro" for a Vinely Pro. A Vinely Pro can only have a mentor.'])
    else:
      # can only set current_pro
      if cleaned_data['mentor']:
        self._errors["mentor"] = ErrorList([u'You can only assign a mentor to a Vinely Pro. %s <%s> is not a Vinely Pro.' % (self.instance.user.get_full_name(), self.instance.user.email)])
    return cleaned_data


class VinelyUserProfileAdmin(admin.ModelAdmin):

  list_display = ('email', 'full_name', 'user_image', 'dob', 'phone', 'zipcode', 'news_optin_flag', 'wine_personality', 'role', 'vinely_pro_email', 'pro_number')  # , 'nearest_pro', )
  list_filter = ('role', MentorAssignedFilter, ProAssignedFilter)
  list_editable = ('wine_personality', )
  raw_id_fields = ('user', 'mentor', 'current_pro')
  model = UserProfile
  form = VinelyUserProfileForm
  actions = [approve_pro, remove_pro_privileges, change_to_host, change_to_taster, cancel_subscription, leave_vinely]
  search_fields = ['user__first_name', 'user__last_name', 'user__email']

  def nearest_pro(self, instance):
    pro = instance.find_nearest_pro()
    return '%s %s <%s>' % (pro.first_name, pro.last_name, pro.email)

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

  def vinely_pro_email(self, instance):
    # need to show the vinely pro
    assigned_pro, assigned_pro_profile = my_pro(instance.user)
    if assigned_pro:
      return assigned_pro.email
    else:
      return None

  def full_name(self, instance):
    return "%s %s" % (instance.user.first_name, instance.user.last_name)

  def pro_number(self, instance):
    return "".join([acc.account_number for acc in VinelyProAccount.objects.filter(users=instance.user)])

  def save_model(self, request, obj, form, change):
    old_profile = UserProfile.objects.get(id=obj.pk)
    if obj.mentor != old_profile.mentor:
      # new pro was assigned, so send e-mail to the host
      send_mentor_assigned_notification_email(request, obj.user, obj.mentor)
      send_mentee_assigned_notification_email(request, obj.mentor, obj.user)
      messages.info(request, "New mentor has been successfully assigned.")

    if obj.current_pro != old_profile.current_pro:
      if obj.is_host():
        send_pro_assigned_notification_email(request, obj.current_pro, obj.user)
        send_host_vinely_party_email(request, obj.user, obj.current_pro)
      messages.info(request, "New pro has been successfully assigned.")

    super(VinelyUserProfileAdmin, self).save_model(request, obj, form, change)

admin.site.register(UserProfile, VinelyUserProfileAdmin)
admin.site.unregister(User)


class VinelyUserAdmin(EmailUserAdmin):

  list_display = ('email', 'first_name', 'last_name', 'user_type', 'zipcode', 'pro_number', 'club_member')
  list_filter = ('groups', 'is_active', 'userprofile__club_member')

  def club_member(self, instance):
    return instance.userprofile.club_member

  def user_type(self, instance):
    return instance.get_profile().get_role_display()

  def zipcode(self, instance):
    zipcode_str = instance.get_profile().zipcode
    return zipcode_str

  def pro_number(self, instance):
    return "".join([acc.account_number for acc in VinelyProAccount.objects.filter(users=instance)])


class SubscriptionAdmin(admin.ModelAdmin):

  list_display = ('email', 'full_name', 'state', 'quantity', 'frequency', 'next_invoice_date', 'updated_datetime')
  search_fields = ('user__email', 'user__first_name', 'user__last_name')
  list_editable = ['next_invoice_date']
  raw_id_fields = ['user']
  actions = [cancel_subscription]

  def get_actions(self, request):
    actions = super(SubscriptionAdmin, self).get_actions(request)
    del actions['delete_selected']
    return actions

  def email(self, instance):
    return instance.user.email

  def state(self, instance):
    return instance.user.get_profile().shipping_address.state

  def full_name(self, instance):
    return "%s %s" % (instance.user.first_name, instance.user.last_name)

  #def response_change(self, request, obj, post_url_continue=None):
  #  return HttpResponseRedirect(reverse("support:manage_subscriptions"))

  def queryset(self, request):
    subscription_ids = []
    for user_id in SubscriptionInfo.objects.exclude(frequency__in=[0, 9]).filter(quantity__gt=0).values_list('user', flat=True).distinct():
      user = User.objects.get(id=user_id)
      subscription = SubscriptionInfo.objects.filter(user=user).order_by('-updated_datetime')[0]
      if not (subscription.frequency in [0, 9] or subscription.quantity == 0):
        subscription_ids.append(subscription.id)

    subscriptions = SubscriptionInfo.objects.filter(id__in=subscription_ids).order_by('next_invoice_date')
    return subscriptions

  def save_model(self, request, obj, form, change):
    # TODO:
    # 1. how to deal with user changing states from admin/my_information
    # 2. Deleting subscriptions from drop down in list_display does not go through model
    receiver = obj.user
    current_shipping = receiver.userprofile.shipping_address
    receiver_state = Zipcode.objects.get(code=current_shipping.zipcode).state

    if form.cleaned_data['frequency'] == 1:
      from_date = datetime.date(timezone.now())
      next_invoice = from_date + relativedelta(months=+1)
    else:
      # set it to yesterday since subscription cancelled or was one time purchase
      # this way, celery task won't pick things up
      next_invoice = timezone.now() - timedelta(days=1)
    obj.next_invoice_date = next_invoice
    obj.save()

    subscription_updated = False
    if receiver_state in Cart.STRIPE_STATES:
      subscription_updated = receiver.userprofile.update_stripe_subscription(form.cleaned_data['frequency'], form.cleaned_data['quantity'])

    if subscription_updated:
      messages.success(request, "Stripe subscription successfully updated.")
    else:
      messages.error(request, "Stripe subscription did not get updated probably because no subscription existed or user does not live in a state handled by Stripe.")

    super(SubscriptionAdmin, self).save_model(request, obj, form, change)


class AddressAdmin(admin.ModelAdmin):
  pass

admin.site.register(User, VinelyUserAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(SubscriptionInfo, SubscriptionAdmin)
