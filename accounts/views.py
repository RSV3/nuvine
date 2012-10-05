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

from main.models import EngagementInterest, PartyInvite, MyHost, Party

from emailusernames.forms import EmailAuthenticationForm, EmailUserChangeForm

from accounts.forms import ChangePasswordForm, VerifyAccountForm, VerifyEligibilityForm, UpdateAddressForm, ForgotPasswordForm,\
                           UpdateSubscriptionForm, PaymentForm, ImagePhoneForm, UserInfoForm, NameEmailUserMentorCreationForm, \
                           HeardAboutForm
from accounts.models import VerificationQueue, SubscriptionInfo, VinelyProAccount
from accounts.utils import send_verification_email, send_password_change_email, send_pro_request_email, send_unknown_pro_email, \
    check_zipcode, send_not_in_area_party_email, send_know_pro_party_email


from main.utils import send_host_vinely_party_email, my_host, my_pro
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

from main.utils import UTC
from datetime import datetime, timedelta
import math

@login_required
def my_information(request):
  """
    Change shipping, billing, payment information
  """

  data = {}

  u = request.user
  profile = u.get_profile()

  user_form = UserInfoForm(request.POST or None, instance=u, prefix='user')
  shipping_form = UpdateAddressForm(request.POST or None, instance=profile.shipping_address, prefix='shipping')
  billing_form = UpdateAddressForm(request.POST or None, instance=profile.billing_address, prefix='billing')
  payment_form = PaymentForm(request.POST or None, instance=profile.credit_card, prefix='payment')
  profile_form = ImagePhoneForm(request.POST or None, request.FILES or None, instance=profile, prefix='profile')
  eligibility_form = VerifyEligibilityForm(request.POST or None, instance=profile, prefix='eligibility')

  user_updated = False
  shipping_updated = False
  billing_updated = False
  payment_updated = False
  profile_updated = False
  eligibility_updated = False
  
  
  if request.method == 'POST':
    today = datetime.date(datetime.now(tz=UTC()))
    dob = today
    try:
      dob = datetime.strptime(request.POST.get('eligibility-dob'), '%Y-%m-%d').date()
    except Exception, e:
      pass
    
    datediff = today - dob
    if (datediff.days < timedelta(math.ceil(365.25 * 21)).days and request.POST.get('eligibility-above_21') == 'on') or \
          (not dob and request.POST.get('eligibility-above_21') == 'on'):
      messages.error(request, 'The Date of Birth shows that you are not over 21')
      return HttpResponseRedirect('.')
      
  if user_form.is_valid(): 
    update_user = user_form.save()
    user_updated = True 

  if shipping_form.is_valid(): 
    shipping_address = shipping_form.save()
    profile.shipping_address = shipping_address
    shipping_updated = True 

  if billing_form.is_valid(): 
    billing_address = billing_form.save()
    profile.billing_address = billing_address
    billing_updated = True 

  if payment_form.is_valid():
    credit_card = payment_form.save()
    profile.credit_card = credit_card
    profile.save()
    payment_updated = True 

  if eligibility_form.is_valid():
    eligible_profile = eligibility_form.save()
    eligibility_updated = True

  if profile_form.is_valid():
    new_profile = profile_form.save()

  if user_updated or shipping_updated or billing_updated or payment_updated or eligibility_updated:
    messages.success(request, 'Your information has been updated on %s.' % datetime.now().strftime("%b %d, %Y at %I:%M %p"))
    data['updated'] = True

  data['user_form'] = user_form
  data['shipping_form'] = shipping_form

  if profile.credit_card and request.method == "GET":
    payment_form.initial['card_number'] = profile.credit_card.decrypt_card_num()

  data['billing_form'] = billing_form
  data['payment_form'] = payment_form
  data['profile_form'] = profile_form
  data['eligibility_form'] = eligibility_form
  data['profile'] = profile

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

  # try:
  #   user_subscription = SubscriptionInfo.objects.get(user=u)
  # except SubscriptionInfo.DoesNotExist:
  #   user_subscription = None
  subscriptions = SubscriptionInfo.objects.filter(user=u)
  if subscriptions.exists():
    user_subscription = subscriptions[0]
  else:
    user_subscription = None
  
  form = UpdateSubscriptionForm(request.POST or None, instance=user_subscription)
  if form.is_valid():
    form.save()
    messages.success(request, "Your subscription will be updated for the next month.")

  data['invited_by'] = my_host(u)
  data['pro_user'], data['pro_profile'] = my_pro(u)
  data['subscriptions'] = subscriptions
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
    send_password_change_email(request, verification_code, temp_password, user)
    data["changed_password"] = True      
    data["email"] = form.cleaned_data['email']

  data['form'] = form
  return render_to_response("accounts/forgot_password.html", data, 
                        context_instance=RequestContext(request))

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def fb_vinely_event(request):
  return vinely_event(request, fb_page=1)

def vinely_event(request, fb_page=0):
  data = {}
  data['fb_view'] = fb_page
  return render_to_response("main/vinely_event.html", data, context_instance=RequestContext(request))

#@csrf_exempt
def fb_vinely_event_signup(request, party_id):
  return vinely_event_signup(request, party_id, 1)

def vinely_event_signup(request, party_id, fb_page=0):
  # Added Oct 2 2012 - Billy
  # Allow taster to signup from FB page
  # if signing up as a taster there must be a party to link to
  account_type = 3
  role = Group.objects.get(id=account_type)
  data = {}
  data['fb_view'] = fb_page
  today = datetime.now(tz=UTC())
  try:
    party = Party.objects.get(pk=party_id, event_date__gte = today)
  except:
    raise Http404

  # create users and send e-mail notifications
  form = NameEmailUserMentorCreationForm(request.POST or None, initial = {'account_type':account_type}) 

  # FB uses post to get page so shouldnt validate

  # raise Exception
  if request.method == 'POST' and request.POST.get('rsvp'):
    if form.is_valid():
      user = form.save()
      profile = user.get_profile()
      profile.zipcode = form.cleaned_data['zipcode']
      ok = check_zipcode(profile.zipcode)
      if not ok:
        messages.info(request, 'Please note that Vinely does not currently operate in your area.')
        send_not_in_area_party_email(request, user, account_type)

      user.groups.add(role)

      user.is_active = False
      temp_password = User.objects.make_random_password()
      user.set_password(temp_password)
      user.save()

      # save engagement type
      engagement_type = account_type 

      interest, created = EngagementInterest.objects.get_or_create(user=user, 
                                                        engagement_type=engagement_type)

      verification_code = str(uuid.uuid4())
      vque = VerificationQueue(user=user, verification_code=verification_code)
      vque.save()

      # send out verification e-mail, create a verification code
      send_verification_email(request, verification_code, temp_password, user.email)

      data["email"] = user.email
      data["first_name"] = user.first_name
      data["account_type"] = account_type
      
      response = int(request.POST['rsvp'])
      # link them to party and RSVP
      PartyInvite.objects.create(party=party, invitee=user, invited_by=party.host, 
                                response=response, response_timestamp=today)

      messages.success(request, "Thank you for your interest in attending a Vinely Party.")

      return render_to_response("accounts/verification_sent.html", data, context_instance=RequestContext(request))

  # data['heard_about_us_form'] = HeardAboutForm()
  data['form'] = form
  data['role'] = role.name
  data['account_type'] = account_type
  data["get_started_menu"] = True

  return render_to_response("main/vinely_event_signup.html", data, context_instance=RequestContext(request))


def sign_up(request, account_type):
  """
    :param account_type: 1 - Vinely Pro 
                          2 - Vinely Host 
                          3 - Vinely Taster 
                          4 - Supplier 
                          5 - Vinely Tasting Lead 
  """

  data = {}
  role = None 

  u = request.user
  account_type = int(account_type)

  pro_group = Group.objects.get(name="Vinely Pro")
  hos_group = Group.objects.get(name="Vinely Host")
  tas_group = Group.objects.get(name="Vinely Taster")
  pro_pending_group = Group.objects.get(name="Pending Vinely Pro")

  # Added Oct 2 2012 - Billy
  # Allow taster to signup from FB page
  # if signing up as a taster there must be a party to link to
  today = datetime.now(tz=UTC())
  if account_type == 3:
    try:
      party_id = int(request.GET.get('p'))
      party = Party.objects.get(pk=party_id, event_date__gte = today)
    except:
      raise Http404

  ### Handle people who are already signed up 
  if u.is_authenticated():
    if pro_group in u.groups.all():
      data["already_signed_up"] = True
      data["get_started_menu"] = True
      return render_to_response("accounts/sign_up.html", data, context_instance=RequestContext(request))
    
    elif hos_group in u.groups.all():
      # can only be pro
      if account_type > 1:
        data["already_signed_up"] = True
        data["get_started_menu"] = True
        ok = check_zipcode(u.get_profile().zipcode)
        if not ok:
          messages.info(request, 'Please note that Vinely does not currently operate in your area.')
          send_not_in_area_party_email(request, u, account_type)
        
      elif account_type == 1:
        EngagementInterest.objects.get_or_create(user=u, engagement_type=account_type)
        ok = check_zipcode(u.get_profile().zipcode)
        if not ok:
          messages.info(request, 'Please note that Vinely does not currently operate in your area.')
          send_not_in_area_party_email(request, u, account_type)
          
        # if not already in pro_pending_group, add them
        if not pro_group in u.groups.all():
          u.groups.clear()
          u.groups.add(pro_pending_group)
          # u.groups.remove(hos_group)
        
        send_pro_request_email(request, u)
        messages.success(request, "Thank you for your interest in becoming a Vinely Pro!")
      return render_to_response("accounts/pro_request_sent.html", data, context_instance=RequestContext(request))
    
    elif tas_group in u.groups.all():
      if account_type == 1 or account_type == 2:
        EngagementInterest.objects.get_or_create(user=u, engagement_type=account_type)
        my_hosts, created = MyHost.objects.get_or_create(pro=None, host=u)
        
        ok = check_zipcode(u.get_profile().zipcode)
        if not ok:
          messages.info(request, 'Please note that Vinely does not currently operate in your area.')
          send_not_in_area_party_email(request, u, account_type)
        
      if account_type == 1:
        send_pro_request_email(request, u)
        # if not already in pro_pending_group, add them
        if not pro_group in u.groups.all():
          u.groups.clear()
          u.groups.add(pro_pending_group)
          #u.groups.remove(tas_group)
        messages.success(request, "Thank you for your interest in becoming a Vinely Pro!")
        return render_to_response("accounts/pro_request_sent.html", data, context_instance=RequestContext(request))
      
      elif account_type == 2:
        send_host_vinely_party_email(request, u) # to vinely
        u.groups.clear()
        u.groups.add(hos_group)
        u.groups.remove(tas_group)
        messages.success(request, "Thank you for your interest in hosting a Vinely Party!")
        return render_to_response("accounts/host_request_sent.html", data, context_instance=RequestContext(request))
        
      elif account_type > 2:
        data["already_signed_up"] = True
        data["get_started_menu"] = True
        return render_to_response("accounts/sign_up.html", data, context_instance=RequestContext(request))               

  ### Handle people who are signing up fresh
  if account_type == 5:
    # people who order wine tasting kit
    role = tas_group 
  elif account_type in [1,2,3]:
    role = Group.objects.get(id=account_type)

  if not role:
    # currently suppliers cannot sign up
    raise Http404

  # create users and send e-mail notifications
  form = NameEmailUserMentorCreationForm(request.POST or None, initial = {'account_type':account_type}) 
  
  if form.is_valid():
    user = form.save()
    profile = user.get_profile()
    profile.zipcode = form.cleaned_data['zipcode']
    ok = check_zipcode(profile.zipcode)
    if not ok:
      messages.info(request, 'Please note that Vinely does not currently operate in your area.')
      send_not_in_area_party_email(request, user, account_type)
      
    # if pro, then mentor IS mentor
    if account_type == 1:
      try:
        # make sure the pro exists
        pro = User.objects.get(email = request.POST.get('mentor'), groups__in = [pro_group])
        profile.mentor = pro
      except Exception, e:
        pass # leave mentor as default
      
    elif account_type == 2:
      # if host, then set mentor to be the host's pro
      try:
        # make sure the pro exists
        pro = User.objects.get(email = request.POST.get('mentor'), groups__in = [pro_group])
          # map host to a pro
        my_hosts, created = MyHost.objects.get_or_create(pro=pro, host=user)
      except Exception, e:
        pass
        # my_hosts, created = MyHost.objects.get_or_create(pro=None, host=user)
    
    profile.save()
    
    if role == pro_group:
      # if requesting to be pro, put them in pending pro group
      user.groups.add(pro_pending_group)
    else:
      user.groups.add(role)

    user.is_active = False
    temp_password = User.objects.make_random_password()
    user.set_password(temp_password)
    user.save()

    # save engagement type
    engagement_type = account_type 

    interest, created = EngagementInterest.objects.get_or_create(user=user, 
                                                      engagement_type=engagement_type)

    verification_code = str(uuid.uuid4())
    vque = VerificationQueue(user=user, verification_code=verification_code)
    vque.save()

    # send out verification e-mail, create a verification code
    send_verification_email(request, verification_code, temp_password, user.email)

    data["email"] = user.email
    data["first_name"] = user.first_name

    data["account_type"] = account_type 
    if account_type == 1:
      send_pro_request_email(request, user)
      messages.success(request, "Thank you for your interest in becoming a Vinely Pro!")
      return render_to_response("accounts/pro_request_sent.html", data, context_instance=RequestContext(request))
    elif account_type == 2:
      # send mail to sales@vinely if no mentor
      mentor_pro = None
      try:
        # make sure selected mentor is a pro
        mentor_pro = User.objects.get(email = request.POST.get('mentor'))
        
        if pro_group in mentor_pro.groups.all():
          send_know_pro_party_email(request, user) # to host
      except User.DoesNotExist, e:
        # mail sales
        send_unknown_pro_email(request, user) # to host
        
      send_host_vinely_party_email(request, user, mentor_pro) # to pro or vinely
      messages.success(request, "Thank you for your interest in hosting a Vinely Party!")

    elif account_type == 3:
      # link them to party and RSVP
      PartyInvite.objects.create(party=party, invitee=user, invited_by=party.host, 
                                response=PartyInvite.RESPONSE_CHOICES[3][0], response_timestamp=today)

      messages.success(request, "Thank you for your interest in attending a Vinely Party.")

    data['heard_about_us_form'] = HeardAboutForm()
    data["get_started_menu"] = True
    return render_to_response("accounts/verification_sent.html", data, context_instance=RequestContext(request))

  data['form'] = form
  data['role'] = role.name
  data['account_type'] = account_type
  data["get_started_menu"] = True

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
      # accepted tos is True
      profile = user.get_profile()
      profile.accepted_tos = True
      profile.save()

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


def terms(request):

  data = {}

  return render_to_response("accounts/terms.html", data,
                                  context_instance=RequestContext(request))


def privacy(request):

  data = {}

  return render_to_response("accounts/privacy.html", data,
                                  context_instance=RequestContext(request))

@login_required
def host_unlink(request):

  data = {}

  u = request.user
  # unlink current user's host 

  return HttpResponseRedirect(reverse("edit_subscription")) 


@login_required
def pro_unlink(request):

  data = {}

  u = request.user
  # unlink current user's pro 

  return HttpResponseRedirect(reverse("edit_subscription")) 
