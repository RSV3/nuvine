# Create your views here.
from urlparse import urlparse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, Template
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from main.models import EngagementInterest, PartyInvite

from emailusernames.forms import EmailAuthenticationForm, NameEmailUserCreationForm

from accounts.forms import ChangePasswordForm, VerifyAccountForm, VerifyEligibilityForm, UpdateAddressForm, ForgotPasswordForm,\
                            MyInformationForm, UpdateSubscriptionForm
from accounts.models import VerificationQueue, SubscriptionInfo
from accounts.utils import send_verification_email, send_password_change_email

import uuid
import logging

from datetime import datetime

log = logging.getLogger(__name__)

@login_required
def profile(request):
  """
    After user logged in
  """
  return HttpResponseRedirect(reverse('home_page'))

@login_required
def my_information(request):
  """
    Change shipping, billing, payment information
  """

  data = {}

  u = request.user
  profile = u.get_profile()

  form = MyInformationForm(request.POST or None, instance=profile)
  if form.is_valid():
    form.save()
    messages.success(request, 'Your information has been updated on %s.' % datetime.now().strftime("%b %d, %Y at %I:%M %p"))

  data['form'] = form
  data['my_information'] = True
  return render_to_response("accounts/my_information.html", data,
                            context_instance=RequestContext(request))


@login_required
def edit_subscription(request):
  """
    Update one's subscription's

    - Cancel
    - Change product
    - Change frequency
  """

  u = request.user

  data = {}
  data['edit_subscription'] = True

  try:
    user_subscription = SubscriptionInfo.objects.get(user=u)
  except SubscriptionInfo.DoesNotExist:
    user_subscription = None

  form = UpdateSubscriptionForm(request.POST or None, instance=user_subscription)
  if form.is_valid():
    form.save()
    messages.success(request, "Your subscription will be updated for the next month.")

  ps_group = Group.objects.get(name="Party Specialist")
  ph_group = Group.objects.get(name="Party Host")
  sp_group = Group.objects.get(name='Supplier')
  at_group = Group.objects.get(name='Attendee')

  if ps_group in u.groups.all():
    data["specialist"] = True
  if ph_group in u.groups.all():
    data["host"] = True
    invitation = PartyInvite.objects.filter(invitee=u).order_by('-invited_timestamp')
    if invitation.exists():
      data['invited_by'] = invitation[0].party.host
    else:
      myspecialists = MyHosts.objects.filter(host=u).order_by('-timestamp')
      if myspecialists.exists():
        data['invited_by'] = myspecialists[0].specialist
        data['specialist_user'] = myspecialists[0].specialist
        data['specialist_profile'] = myspecialists[0].specialist.get_profile()
  if sp_group in u.groups.all():
    data["supplier"] = True
  if at_group in u.groups.all():
    data["attendee"] = True
    # find specialist and host who invited first
    invitation = PartyInvite.objects.filter(invitee=u).order_by('-invited_timestamp')
    if invitation.exists():
      data['invited_by'] = invitation[0].party.host
      myspecialists = MyHosts.objects.filter(host=data['invited_by']).order_by('-timestamp')
      if myspecialists.exists():
        data['invited_by'] = myspecialists[0].specialist
        data['specialist_user'] = myspecialists[0].specialist
        data['specialist_profile'] = myspecialists[0].specialist.get_profile()
    else:
      # no parties, so no specialists
      pass

  if user_subscription is None:
    form.initial['user'] = u
  data['form'] = form

  return render_to_response("accounts/edit_subscription.html", data, context_instance=RequestContext(request))

@login_required
def change_password(request):

  data = {}

  u = request.user

  form = ChangePasswordForm(request.POST or None)
  if form.is_valid():
    # set password
    u.set_password(form.cleaned_data['new_password'])
    u.save()

    messages.success(request, 'Your password has been updated on %s.' % datetime.now().strftime("%b %d, %Y at %I:%M %p"))

  form.initial['email'] = u.email
  data["form"] = form
  data['change_password'] = True
  return render_to_response("accounts/change_password.html", data, 
                        context_instance=RequestContext(request))

def forgot_password(request):

  data = {}

  form = ForgotPasswordForm(request.POST or None)
  if form.is_valid():
    # find user with this e-mail and assign temporary password
    user = User.objects.get(email = form.cleaned_data['email'])
    temp_password = User.objects.make_random_password()
    user.set_password(temp_password)
    user.save()

    verification_code = str(uuid.uuid4())
    vque = VerificationQueue(user=user, verification_code=verification_code, verification_type=VerificationQueue.VERIFICATION_CHOICES[1][0])
    vque.save()

    # send an e-mail with random password
    send_password_change_email(request, verification_code, temp_password, user.email)
    data["changed_password"] = True      
    data["email"] = form.cleaned_data['email']

  data['form'] = form
  return render_to_response("accounts/forgot_password.html", data, 
                        context_instance=RequestContext(request))

def sign_up(request, account_type):
  """
    :param account_type: 0 - party specialist
                          1 - party host
                          2 - party attendees
                          3 - supplier
                          4 - tasting lead
  """

  data = {}
  role = ""

  account_type = int(account_type)
  if account_type == 0:
    role = "Party Specialist"
  elif account_type == 1:
    role = "Party Host"
  elif account_type == 2:
    role = "Attendee"
  elif account_type == 3:
    role = "Supplier"
  elif account_type == 4:
    # people who order wine tasting kit
    role = "Attendee"

  if not role:
    raise Http404

  # create users and send e-mail notifications
  form = NameEmailUserCreationForm(request.POST or None) 

  if form.is_valid():
    user = form.save()

    user.groups.add(Group.objects.get(name=role))

    user.is_active = False
    temp_password = User.objects.make_random_password()
    user.set_password(temp_password)
    user.save()

    # save engagement type
    engagement_type = 2
    if account_type == 1:
      engagemnt_type = 0
    elif account_type == 0:
      engagement_type = 1
    elif account_type == 2:
      engagement_type = 2
    elif account_type == 4:
      engagement_type = 3

    interest, created = EngagementInterest.objects.get_or_create(user=user, 
                                                      engagement_type=EngagementInterest.ENGAGEMENT_CHOICES[engagement_type][0])

    verification_code = str(uuid.uuid4())
    vque = VerificationQueue(user=user, verification_code=verification_code)
    vque.save()

    # send out verification e-mail, create a verification code
    send_verification_email(request, verification_code, temp_password, user.email)

    data["email"] = user.email

    data["account_type"] = account_type 
    if account_type == 1:
      messages.success(request, "Thank you for your interest in hosting a Vinely Party!")

    return render_to_response("accounts/verification_sent.html", data, context_instance=RequestContext(request))

  data['form'] = form
  data['role'] = role
  data['account_type'] = account_type

  return render_to_response("accounts/sign_up.html", data,
                        context_instance=RequestContext(request))

def verify_email(request, verification_code):
  """
    Verify e-mail, used when user changes e-mail address
  """
  data = {}

  try:
    verify = VerificationQueue.objects.get(verification_code=verification_code, verified=False,
                                          verification_type=VerificationQueue.VERIFICATION_CHOICES[2][0])
    old_email = verify.user.email

    user = verify.user
    user.email = verify.verify_data
    user.save()

    verify.verified = True
    verify.save()

    messages.success(request, "Your new e-mail %s has been verified and old e-mail %s removed."%(user.email, old_email))

    return render_to_response("accounts/verified_email.html", data, context_instance=RequestContext(request))
  except VerificationQueue.DoesNotExist:
    raise PermissionDenied

def verify_account(request, verification_code):
  """
    Show e-mail and ask to verify
   
    Ask to type temporary password and set new password
  """

  data = {}

  data["verification_code"] = verification_code 

  try:
    verification = VerificationQueue.objects.get(verification_code=verification_code)
    if verification.verified:
      data["error"] = "You have already been verified"
    else:
      data["email"] = verification.user.email
  except VerificationQueue.DoesNotExist:
    data["error"] = "Verification code is not valid"
  
  if "error" not in data:
    form = VerifyAccountForm(request.POST or None)
    if form.is_valid():
      verification.verified = True
      verification.save()

      # activate user
      user = verification.user
      user.set_password(form.cleaned_data['new_password'])
      user.is_active = True
      user.save()

      user = authenticate(email=user.email, password=form.cleaned_data['new_password'])
      if user is not None:
        login(request, user)
      else:
        log.debug("For some reason %s could not be verified and authenticated."%user.email)
        return HttpResponseRedirect(reverse("login")) 

      if verification.verification_type == VerificationQueue.VERIFICATION_CHOICES[0][0]:
        messages.success(request, "Your account has been verified and now is active.")
      elif verification.verification_type == VerificationQueue.VERIFICATION_CHOICES[1][0]:
        messages.success(request, "Your password has been reset to your new password.")

      return HttpResponseRedirect(reverse("home_page"))

    form.initial['email'] = verification.user.email
    data["form"] = form

  return render_to_response("accounts/verify_account.html", data,
                        context_instance=RequestContext(request))

@login_required
def verify_eligibility(request):
  """
    Personal information to apply for application
  """
  data = {}

  # TODO: Need to make the user enter home address and add that to party address
  u = request.user
  profile = u.get_profile()

  form = VerifyEligibilityForm(request.POST or None, instance=profile)
  if form.is_valid():
    form.save()
    messages.success(request, "Your information has been updated on %s." % datetime.now().strftime("%b %d, %Y at %I:%M %p"))

  data["form"] = form
  data['verify_eligibility'] = True

  return render_to_response("accounts/verify_eligibility.html", data,
                                  context_instance=RequestContext(request))



