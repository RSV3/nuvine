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

from emailusernames.forms import EmailAuthenticationForm, NameEmailUserCreationForm

from accounts.forms import ChangePasswordForm, VerifyAccountForm, VerifyEligibilityForm, UpdateAddressForm 
from accounts.models import VerificationQueue
from accounts.utils import send_verification_email

import uuid
import logging

log = logging.getLogger(__name__)

@login_required
def profile(request):
  """
    After user logged in
  """
  return HttpResponseRedirect(reverse('home_page'))

@login_required
def change_password(request):

  data = {}

  u = request.user

  form = ChangePasswordForm(request.POST or None)
  if form.is_valid():
    # set password
    u.set_password(form.cleaned_data['new_password'])
    u.save()

    messages.success(request, 'Password has been updated')

  form.initial['email'] = u.email
  data["form"] = form
  return render_to_response("accounts/change_password.html", data, 
                        context_instance=RequestContext(request))

@login_required
def settings(request):
  """
    User settings
  """
  data = {}

  return render_to_response("accounts/settings.html", data, 
                        context_instance=RequestContext(request))

def sign_up(request, account_type):
  """
    :param account_type: 0 - party specialist
                          1 - party host
                          2 - party attendees
                          3 - supplier
  """

  data = {}
  role = ""
  if int(account_type) == 0:
    role = "Party Specialist"
  elif int(account_type) == 1:
    role = "Party Host"
  elif int(account_type) == 2:
    role = "Attendee"
  elif int(account_type) == 3:
    role = "Supplier"
  elif int(account_type) == 4:
    role = "Tasting"

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

    verification_code = str(uuid.uuid4())
    vque = VerificationQueue(user=user, verification_code=verification_code)
    vque.save()

    # send out verification e-mail, create a verification code
    send_verification_email(request, verification_code, temp_password, user.email)

    return render_to_response("accounts/verification_sent.html", c, context_instance=RequestContext(request))

  data['form'] = form
  data['role'] = role
  data['account_type'] = account_type

  return render_to_response("accounts/sign_up.html", data,
                        context_instance=RequestContext(request))

def verify_email(request, verification_code):
  """
    Verify e-mail
  """
  data = {}

  verify = VerificationQueue.objects.get(verification_code=verification_code)
  data['email'] = verify.user.email
  user = verify.user
  user.is_active = True
  user.save()

  verify.delete()

  return render_to_response("accounts/verified_email.html", data,
                        context_instance=RequestContext(request))

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

      # TODO: show an alert and send to home page

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

  form = VerifyEligibilityForm(request.POST or None)
  if form.is_valid():
    form.save()

  form.initial['user'] = request.user
  data["form"] = form

  return render_to_response("accounts/verify_eligibility.html", data,
                                  context_instance=RequestContext(request))

@login_required
def update_addresses(request):
  """
    Update your addresses 
  """
  data = {}

  # TODO: Need to make the user enter home address and add that to party address

  form = UpdateAddressForm(request.POST or None)
  if form.is_valid():
    form.save()

  data["form"] = form

  return render_to_response("accounts/update_addresses.html", data,
                                  context_instance=RequestContext(request))



