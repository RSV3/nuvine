# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings

from main.models import EngagementInterest, PartyInvite, MyHost, ProSignupLog, CustomizeOrder, Cart

from accounts.forms import ChangePasswordForm, VerifyAccountForm, VerifyEligibilityForm, UpdateAddressForm, ForgotPasswordForm,\
                            UpdateSubscriptionForm, PaymentForm, ImagePhoneForm, UserInfoForm, NameEmailUserMentorCreationForm, \
                            HeardAboutForm, MakeHostProForm, ProLinkForm, MakeTasterForm, NewHostProForm, AgeValidityForm, \
                            VinelyEmailAuthenticationForm
from accounts.models import VerificationQueue, SubscriptionInfo, Zipcode
from accounts.utils import send_verification_email, send_password_change_email, send_pro_request_email, send_unknown_pro_email, \
                            check_zipcode, send_not_in_area_party_email, send_know_pro_party_email, send_account_activation_email, \
                            get_default_pro

from cms.models import ContentTemplate
from main.utils import send_host_vinely_party_email, my_host, my_pro

from stripecard.models import StripeCard

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import math

import uuid
import logging
import stripe

log = logging.getLogger(__name__)


# @login_required
# def logout(request):
#   u = request.user
#   profile = u.get_profile()
#   profile.last_page = request.GET.get('next')
#   profile.save()
#   auth.logout(request)

#   return HttpResponseRedirect('/')

@login_required
def delete_card(request):
  u = request.user
  profile = u.get_profile()

  profile.credit_card = None
  profile.stripe_card = None
  profile.save()
  u.get_profile().cancel_subscription()
  return HttpResponseRedirect(reverse('my_information'))


@login_required
def profile(request):
  """
    After user logged in
  """
  u = request.user
  profile = u.get_profile()

  if profile.is_taster():
    # if you have new RSVP not responded to
    invites = PartyInvite.objects.filter(invitee=u, response=0, party__event_date__gte=timezone.now()).order_by('party__event_date')
    if invites.exists():
      invite = invites[0]
      return HttpResponseRedirect(reverse('party_rsvp', args=[invite.rsvp_code, invite.party.id]))
    else:
      return HttpResponseRedirect(reverse('home_page'))
  else:
    return HttpResponseRedirect(reverse('home_page'))


@login_required
def fix_my_picture(request):
  data = {}

  u = request.user
  profile = u.get_profile()
  # print profile.image.url

  initial_profile = {'dob': profile.dob.strftime("%m/%d/%Y") if profile.dob else ''}

  user_form = UserInfoForm(request.POST or None, instance=u, prefix='user')
  shipping_form = UpdateAddressForm(request.POST or None, instance=profile.shipping_address, prefix='shipping')
  # billing_form = UpdateAddressForm(request.POST or None, instance=profile.billing_address, prefix='billing')
  payment_form = PaymentForm(request.POST or None, prefix='payment')
  profile_form = ImagePhoneForm(request.POST or None, request.FILES or None, instance=profile, prefix='profile')
  eligibility_form = VerifyEligibilityForm(request.POST or None, instance=profile, initial=initial_profile, prefix='eligibility')

  if profile_form.is_valid():
    profile = profile_form.save()
    # print profile.image.url

    msg = 'Your information has been updated'
    messages.success(request, msg)

  data['profile'] = profile
  data['user_form'] = user_form
  data['shipping_form'] = shipping_form
  # data['billing_form'] = billing_form
  data['payment_form'] = payment_form
  data['profile_form'] = profile_form
  data['eligibility_form'] = eligibility_form

  card_number = 'No card currently on file'
  if profile.stripe_card and profile.shipping_address and (profile.shipping_address.state in Cart.STRIPE_STATES):
    card_number = '*' * 12 + profile.stripe_card.last_four
    #payment_form.initial['card_number'] = card_number
  elif profile.credit_card:
    #payment_form.initial['card_number'] = profile.credit_card.decrypt_card_num()
    card_number = '*' * 12 + profile.credit_card.last_four()

  data['card_number'] = card_number
  return render_to_response("accounts/my_information_test.html", data, context_instance=RequestContext(request))


@login_required
def my_information(request):
  """
    Change shipping, billing, payment information
  """

  data = {}

  u = request.user
  profile = u.get_profile()

  initial_profile = {'dob': profile.dob.strftime("%m/%d/%Y") if profile.dob else ''}
  user_form = UserInfoForm(request.POST if request.POST.get('user_form') else None, instance=u, prefix='user')
  shipping_form = UpdateAddressForm(request.POST if request.POST.get('shipping_form') else None, instance=profile.shipping_address, prefix='shipping')
  # billing_form = UpdateAddressForm(request.POST or None, instance=profile.billing_address, prefix='billing')
  payment_form = PaymentForm(request.POST if request.POST.get('payment_form') else None, prefix='payment')
  profile_form = ImagePhoneForm(request.POST if request.POST.get('user_form') else None, instance=profile, prefix='profile')
  eligibility_form = VerifyEligibilityForm(request.POST if request.POST.get('eligibility_form') else None, instance=profile, initial=initial_profile, prefix='eligibility')

  data['user_form'] = user_form
  data['shipping_form'] = shipping_form
  # data['billing_form'] = billing_form
  data['profile_form'] = profile_form
  data['eligibility_form'] = eligibility_form
  data['payment_form'] = payment_form

  # tracking payment information error
  payment_info_error = False

  if request.method == 'POST':

    # user_form is already validated up-top
    msg = 'Your information has been updated'

    if request.POST.get('user_form'):
      if user_form.is_valid() and profile_form.is_valid():
        updated_user = user_form.save()
        profile = profile_form.save()
        messages.success(request, msg)
      else:
        messages.error(request, 'Errors were encountered when trying to update your information. Please correct them and retry the update.')

    # eligibility_form is already validated up-top
    if request.POST.get('eligibility_form'):
      if eligibility_form.is_valid():
        today = datetime.date(timezone.now())
        dob = eligibility_form.cleaned_data['dob']

        if dob:
          datediff = today - dob
          if (datediff.days < timedelta(math.ceil(365.25 * 21)).days and eligibility_form.cleaned_data['above_21'] == 'on') or \
                (not dob and eligibility_form.cleaned_data['above_21'] == 'on'):
            messages.error(request, 'The Date of Birth shows that you are not over 21')
            return HttpResponseRedirect('.')

        eligibility_form.save()
        messages.success(request, msg)
      else:
        messages.error(request, 'Errors were encountered when trying to update your information. Please correct them and retry the update.')

    if request.POST.get('shipping_form'):
      if shipping_form.is_valid():
        shipping_form.user_profile = profile
        shipping_form.save()
        messages.success(request, msg)
      else:
        messages.error(request, 'Errors were encountered when trying to update your information. Please correct them and retry the update.')

    # if billing_form.is_valid():
    #   billing_form.user_profile = profile
    #   if billing_form.cleaned_data['same_as_shipping']:
    #     profile.billing_address = shipping_address
    #     billing_form = UpdateAddressForm(instance=shipping_address, prefix='billing')
    #   else:
    #     billing_address = billing_form.save()
    #     profile.billing_address = billing_address
    #   billing_updated = True
    # else:
    #   # check if same_as_shipping is true
    #   if request.POST.get('billing-same_as_shipping') and shipping_address:
    #     profile.billing_address = shipping_address
    #     billing_form = UpdateAddressForm(instance=shipping_address, prefix='billing')
    #     billing_updated = True

    if request.POST.get('payment_form'):
      if payment_form.is_valid():
        payment = payment_form.cleaned_data

        receiver_state = 'NONE'
        try:
          if u.userprofile.shipping_address:
            receiver_state = Zipcode.objects.get(code=u.userprofile.shipping_address.zipcode).state
          #else:
          #  receiver_state = Zipcode.objects.get(code=payment['billing_zipcode']).state
        except Zipcode.DoesNotExist:
          pass
        if receiver_state in Cart.STRIPE_STATES:
          if receiver_state == 'MI':
            stripe.api_key = settings.STRIPE_SECRET
          elif receiver_state == 'CA':
            stripe.api_key = settings.STRIPE_SECRET_CA
          stripe_card = profile.stripe_card

          card = {'number': payment['card_number'], 'exp_month': payment['exp_month'], 'exp_year': payment['exp_year'],
                  'cvc': payment['verification_code'], 'name': '%s %s' % (updated_user.first_name, updated_user.last_name),
                  'address_zip': payment['billing_zipcode'],
                  }
          try:
            customer = stripe.Customer.retrieve(id=stripe_card.stripe_user)
            if customer.get('deleted'):
              raise Exception('Customer Deleted')

            # if exists update it in stripe and update entry in StripeCard
            customer.email = updated_user.email
            customer.card = card
            customer.save()

            active_card = customer.active_card
            if active_card.last4 != stripe_card.last_four or active_card.exp_year != stripe_card.exp_year or \
                active_card.exp_month != stripe_card.exp_month or active_card.type != stripe_card.card_type or \
                active_card.address_zip != stripe_card.billing_zipcode:
              stripe_card.exp_month = customer.active_card.exp_month
              stripe_card.exp_year = customer.active_card.exp_year
              stripe_card.last_four = customer.active_card.last4
              stripe_card.card_type = customer.active_card.type
              stripe_card.billing_zipcode = customer.active_card.address_zip
              stripe_card.save()
          except Exception, e:
            # print 'error', e
            log.errors(request, e)
            # no record of this customer-card mapping so create
            try:
              customer = stripe.Customer.create(card=card, email=updated_user.email)
              # create on vinely
              stripe_card = StripeCard.objects.create(stripe_user=customer.id, exp_month=customer.active_card.exp_month,
                                      exp_year=customer.active_card.exp_year, last_four=customer.active_card.last4,
                                      card_type=customer.active_card.type, billing_zipcode=customer.active_card.address_zip)
              profile.stripe_card = stripe_card
              profile.save()
              profile.stripe_cards.add(stripe_card)

            except:
              messages.error(request, 'Your card was declined. In case you are in testing mode please use the test credit card.')
              # return render_to_response("accounts/my_information.html", data, context_instance=RequestContext(request))
        else:
          # if not a stripe state
          credit_card = payment_form.save()
          profile.credit_card = credit_card
          profile.stripecard = None
          profile.save()

        # reset payment form after saving
        data['payment_form'] = PaymentForm(prefix='payment')
      else:
        # if payment form is not valid
        if len(request.POST.get("payment-card_number", '')) == 0:
          # just present empty form since nothing was entered
          data['payment_form'] = PaymentForm(prefix='payment')
        else:
          payment_info_error = True
          messages.error(request, 'Errors were encountered when trying to update your information. Please correct them and retry the update.')

      if not payment_info_error:
        msg = 'Your information has been updated on %s.' % timezone.now().strftime("%b %d, %Y at %I:%M %p")
        messages.success(request, msg)

  card_number = 'No card currently on file'
  if profile.stripe_card and profile.shipping_address and (profile.shipping_address.state in Cart.STRIPE_STATES):
    card_number = '*' * 12 + profile.stripe_card.last_four
  elif profile.credit_card:
    card_number = '*' * 12 + profile.credit_card.last_four()
  # else:
  #   print "No card info"
  data['card_number'] = card_number

  data['profile'] = profile

  return render_to_response("accounts/my_information.html", data, context_instance=RequestContext(request))


@login_required
def edit_subscription(request):
  """
    Update one's subscription's

    - Cancel
    - Change product
    - Change frequency
    - Change Wine mix preferences
  """

  u = request.user

  data = {}
  data['edit_subscription'] = True
  data['pro_link_form'] = ProLinkForm()

  # try:
  #   user_subscription = SubscriptionInfo.objects.get(user=u)
  # except SubscriptionInfo.DoesNotExist:
  #   user_subscription = None
  subscriptions = SubscriptionInfo.objects.filter(user=u).order_by("-updated_datetime")
  if subscriptions.exists():
    user_subscription = subscriptions[0]
  else:
    user_subscription = None

  try:
    custom_order = CustomizeOrder.objects.get(user=u)
    wine_mix = custom_order.wine_mix
    sparkling = custom_order.sparkling
  except CustomizeOrder.DoesNotExist:
    wine_mix = None
    sparkling = None

  initial_data = {'wine_mix': wine_mix, 'sparkling': sparkling}
  initial_data['quantity'] = user_subscription.quantity if user_subscription else 0
  initial_data['frequency'] = user_subscription.frequency if user_subscription else 9

  form = UpdateSubscriptionForm(request.POST or None, instance=user_subscription, initial=initial_data)
  if form.is_valid():
    if not u.userprofile.has_personality():
      data['form'] = form
      messages.warning(request, "You need to first participate in a tasting party to find out your wine personality.")
      return render_to_response("accounts/edit_subscription.html", data, context_instance=RequestContext(request))

    if not u.userprofile.credit_card and not u.userprofile.stripe_card:
      data['form'] = form
      messages.warning(request, "You have no credit card on file yet to order. Please go to the shop page to complete the order process.")
      return render_to_response("accounts/edit_subscription.html", data, context_instance=RequestContext(request))

    if not u.userprofile.shipping_address:
      data['form'] = form
      messages.warning(request, "You need to update your shipping address before you can make a subscription.")
      return render_to_response("accounts/edit_subscription.html", data, context_instance=RequestContext(request))

    # create new subscription info object to track subscription change
    info = SubscriptionInfo(user=u, frequency=form.cleaned_data['frequency'],
                              quantity=form.cleaned_data['quantity'])

    if form.cleaned_data['frequency'] == 1:
      from_date = datetime.date(timezone.now())
      next_invoice = from_date + relativedelta(months=+1)
    else:
      # set it to yesterday since subscription cancelled or was one time purchase
      # this way, celery task won't pick things up
      next_invoice = timezone.now() - timedelta(days=1)
    info.next_invoice_date = next_invoice
    info.save()

    custom_order, created = CustomizeOrder.objects.get_or_create(user=u)
    custom_order.wine_mix = form.cleaned_data['wine_mix']
    custom_order.sparkling = form.cleaned_data['sparkling']
    custom_order.save()
    messages.success(request, "Your subscription will be updated for the next month.")

    current_shipping = u.userprofile.shipping_address
    user_state = Zipcode.objects.get(code=current_shipping.zipcode).state

    subscription_updated = False
    if user_state in Cart.STRIPE_STATES:
      subscription_updated = u.userprofile.update_stripe_subscription(form.cleaned_data['frequency'], form.cleaned_data['quantity'])

      if subscription_updated:
        messages.success(request, "Stripe subscription successfully updated.")
      else:
        messages.error(request, "Stripe subscription did not get updated probably because no subscription existed or user does not live in a state handled by Stripe.")

  data['invited_by'] = my_host(u)

  data['pro_user'] = u.get_profile().current_pro
  data['subscription'] = user_subscription
  data['edit_subscription'] = True
  if user_subscription is None:
    form.initial['user'] = u
  data['form'] = form

  return render_to_response("accounts/edit_subscription.html", data, context_instance=RequestContext(request))


@login_required
def cancel_subscription(request):
  u = request.user
  u.get_profile().cancel_subscription()
  messages.success(request, "Your subscription has been cancelled.")
  return HttpResponseRedirect(reverse("edit_subscription"))


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

  if request.user.is_authenticated():
    return render_to_response("accounts/already_authenticated.html", data,
                              context_instance=RequestContext(request))

  form = ForgotPasswordForm(request.POST or None)
  if form.is_valid():
    # find user with this e-mail and assign temporary password
    user = User.objects.get(email=form.cleaned_data['email'])
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


def activate_account(request):

  data = {}

  if request.user.is_authenticated():
    return render_to_response("accounts/already_authenticated.html", data,
                              context_instance=RequestContext(request))

  form = ForgotPasswordForm(request.POST or None)
  if form.is_valid():
    # find user with this e-mail and assign temporary password
    user = User.objects.get(email=form.cleaned_data['email'])
    temp_password = User.objects.make_random_password()
    user.set_password(temp_password)
    user.save()

    verification_code = str(uuid.uuid4())
    vque = VerificationQueue(user=user, verification_code=verification_code, verification_type=VerificationQueue.VERIFICATION_CHOICES[1][0])
    vque.save()

    # send an e-mail with random password
    send_account_activation_email(request, verification_code, temp_password, user)
    data["changed_password"] = True
    data["email"] = form.cleaned_data['email']

  data['form'] = form
  return render_to_response("accounts/activate_account.html", data,
                        context_instance=RequestContext(request))


# @login_required
def make_pro_host(request, account_type, data):
  '''
  account_type: 'host' or 'pro'
  '''

  data['role'] = account_type

  data['account_type'] = account_type

  u = request.user
  profile = u.get_profile()

  hos_group = Group.objects.get(name="Vinely Host")
  # tas_group = Group.objects.get(name="Vinely Taster")
  pro_pending_group = Group.objects.get(name="Pending Vinely Pro")

  pro, pro_profile = my_pro(u)
  pro_email = pro.email if pro else None
  initial_data = {'account_type': account_type, 'first_name': u.first_name, 'last_name': u.last_name,
                  'email': u.email, 'zipcode': profile.zipcode, 'phone_number': profile.phone, 'mentor': pro_email}

  form = MakeHostProForm(request.POST or None, initial=initial_data)

  data['form'] = form

  if form.is_valid():
    user = form.save(commit=False)
    u.first_name = user.first_name
    u.last_name = user.last_name
    u.save()
    profile = u.get_profile()
    profile.zipcode = form.cleaned_data.get('zipcode')
    profile.phone = form.cleaned_data.get('phone')
    profile.save()

    ### Handle people who are already signed up
    if profile.is_pro():
      data["already_signed_up"] = True
      data["get_started_menu"] = True
      return HttpResponseRedirect(reverse('make_pro'))
      # if account_type == 1:
      #   return render_to_response("accounts/make_host_pro_signup.html", data, context_instance=RequestContext(request))
      # else:
      #   return render_to_response("accounts/make_host.html", data, context_instance=RequestContext(request))

    elif profile.is_host():

      # can only become a pro since user is a host
      if account_type > 1:
        data["already_signed_up"] = True
        data["get_started_menu"] = True
        ok = check_zipcode(profile.zipcode)
        if not ok:
          messages.info(request, 'Please note that Vinely does not currently operate in your area.')
          send_not_in_area_party_email(request, u, account_type)

      elif account_type == 1:
        data['make_host_or_pro'] = True
        EngagementInterest.objects.get_or_create(user=u, engagement_type=account_type)
        # if mentor_email is blank then delink the pro and set to default pro
        try:
          mentor_email = form.cleaned_data.get('mentor')
          if mentor_email:
            mentor = User.objects.get(email=mentor_email)
          else:
            mentor = get_default_pro()
          profile.mentor = mentor
          # no longer taster or host so set current_pro to None
          profile.current_pro = None
          profile.save()
        except User.DoesNotExist:
          mentor = None

        ProSignupLog.objects.get_or_create(new_pro=u, mentor=mentor, mentor_email=form.cleaned_data['mentor'])

        ok = check_zipcode(profile.zipcode)
        if not ok:
          messages.info(request, 'Please note that Vinely does not currently operate in your area.')
          send_not_in_area_party_email(request, u, account_type)

        # if not already in pro_pending_group, add them
        if not u.userprofile.is_pending_pro():
          u.groups.clear()
          u.groups.add(pro_pending_group)

        send_pro_request_email(request, u)
        # messages.success(request, "Thank you for your interest in becoming a Vinely Pro!")
      # return render_to_response("accounts/pro_request_sent.html", data, context_instance=RequestContext(request))
      messages.success(request, "To ensure that Vinely emails get to your inbox, please add info@vinely.com to your email Address Book or Safe List.")
      return HttpResponseRedirect(reverse('home_page'))

    elif profile.is_taster():
      data['make_host_or_pro'] = True

      EngagementInterest.objects.get_or_create(user=u, engagement_type=account_type)

      ok = check_zipcode(profile.zipcode)
      if not ok:
        messages.info(request, 'Please note that Vinely does not currently operate in your area.')
        send_not_in_area_party_email(request, u, account_type)

      if account_type == 1:
        # become a pro
        try:
          mentor_email = form.cleaned_data.get('mentor')
          if mentor_email:
            mentor = User.objects.get(email=mentor_email)
          else:
            mentor = get_default_pro()
          profile.mentor = mentor
          # since no longer host or taster
          profile.current_pro = None
          profile.save()
        except User.DoesNotExist:
          mentor = None

        ProSignupLog.objects.get_or_create(new_pro=u, mentor=mentor, mentor_email=form.cleaned_data['mentor'])

        send_pro_request_email(request, u)
        # if not already in pro_pending_group, add them
        if not u.userprofile.is_pending_pro():
          u.groups.clear()
          u.groups.add(pro_pending_group)
        messages.success(request, "To ensure that Vinely emails get to your inbox, please add info@vinely.com to your email Address Book or Safe List.")
        return HttpResponseRedirect(reverse('home_page'))

      elif account_type == 2:
        # become a host
        try:
          mentor_email = form.cleaned_data.get('mentor')
          # host does not get assigned to anybody if they don't enter pro e-mail 3/10/2013
          pro = User.objects.get(email=mentor_email)
          profile.current_pro = pro
          profile.save()
          send_know_pro_party_email(request, u)  # to host
        except User.DoesNotExist:
          pro = None
          send_unknown_pro_email(request, u)  # to host

        send_host_vinely_party_email(request, u, pro)  # to vinely and the mentor pro
        # send_signed_up_as_host_email(request, u)  # to the current user

        u.groups.clear()
        u.groups.add(hos_group)
        messages.success(request, "To ensure that Vinely emails get to your inbox, please add info@vinely.com to your email Address Book or Safe List.")
        return HttpResponseRedirect(reverse('home_page'))

      elif account_type > 2:
        data["already_signed_up"] = True
        data["get_started_menu"] = True

  if account_type == 1:
    return render_to_response("accounts/make_pro.html", data, context_instance=RequestContext(request))
  else:
    return render_to_response("accounts/make_host_pro_signup.html", data, context_instance=RequestContext(request))


def make_host(request, state=None):
  data = {}
  u = request.user

  if state not in ['people', 'place', 'order', 'rewards', 'signup']:
    state = 'overview'

  data['state'] = state

  if state == 'signup':
    data['host_party_menu'] = True
    if u.is_authenticated():
      return make_pro_host(request, 2, data)
    else:
      return sign_up(request, 2, data)
  else:
    host_sections = ContentTemplate.objects.get(key='make_host').sections.all()
    data['heading'] = host_sections.get(key='header').content
    data['sub_heading'] = host_sections.get(key='sub_header').content
    data['content'] = host_sections.get(key=state).content
    data['host_party_menu'] = True
    return render_to_response("accounts/make_host.html", data, context_instance=RequestContext(request))


def make_pro(request, state=None):
  data = {}
  u = request.user

  if state not in ['parties', 'earnings', 'support', 'growth', 'signup']:
    state = 'overview'

  data['state'] = state

  if state == 'signup':
    data['become_pro_menu'] = True
    if u.is_authenticated():
      return make_pro_host(request, 1, data)
    else:
      return sign_up(request, 1, data)
  else:
    pro_sections = ContentTemplate.objects.get(key='make_pro').sections.all()
    data['heading'] = pro_sections.get(key='header').content
    data['sub_heading'] = pro_sections.get(key='sub_header').content
    data['content'] = pro_sections.get(key=state).content
    data['become_pro_menu'] = True
    return render_to_response("accounts/make_pro.html", data, context_instance=RequestContext(request))


def make_taster(request, rsvp_code):
  # data = {}

  success_url = request.GET.get('next') if request.GET.get('next') else reverse('home_page')

  try:
    user = PartyInvite.objects.get(rsvp_code=rsvp_code).invitee
  except:
    messages.error(request, 'We could not find your information in the system. Please contact <a href="mailto:care@vinely.com">care@vinely.com</a>')
    return HttpResponseRedirect(success_url)

  form = MakeTasterForm(request.POST or None, initial={'account_type': 3}, instance=user)
  err = ""
  if form.is_valid():
    user.set_password(form.cleaned_data['password1'])
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    user.email = form.cleaned_data['email']
    user.is_active = True
    user.save()

    profile = user.get_profile()
    profile.zipcode = form.cleaned_data['zipcode']
    profile.phone = form.cleaned_data['phone_number']
    ok = check_zipcode(profile.zipcode)

    # prevent popping up signup screen again
    guest_rsvp_key = '%s_guest_rsvp' % rsvp_code
    request.session[guest_rsvp_key] = True

    if not ok:
      messages.info(request, 'Please note that Vinely does not currently operate in your area.')
      send_not_in_area_party_email(request, user, 3)

    user = authenticate(email=user.email, password=form.cleaned_data['password1'])
    if user is not None:
      login(request, user)
  else:
    if form.errors['email']:
      err = "?err=1&email=" + request.POST.get('email')
    else:
      messages.error(request, form.errors)
  return HttpResponseRedirect(success_url + err)


def sign_up(request, account_type, data):
  """
    :param account_type:  1 - Vinely Pro
                          2 - Vinely Host
                          3 - Vinely Taster
  """
  # data = {}
  role = None

  account_type = int(account_type)

  pro_group = Group.objects.get(name="Vinely Pro")
  hos_group = Group.objects.get(name="Vinely Host")
  tas_group = Group.objects.get(name="Vinely Taster")
  pro_pending_group = Group.objects.get(name="Pending Vinely Pro")

  if account_type == 1:
    role = pro_group
  elif account_type == 2:
    role = hos_group
  elif account_type == 3:
    role = tas_group

  # create users and send e-mail notifications
  form = NewHostProForm(request.POST or None, initial={'account_type': account_type})

  if form.is_valid():
    user = form.save()
    profile = user.get_profile()
    profile.zipcode = form.cleaned_data['zipcode']
    profile.phone = form.cleaned_data['phone_number']
    ok = check_zipcode(profile.zipcode)

    if not ok:
      messages.info(request, 'Please note that Vinely does not currently operate in your area.')
      send_not_in_area_party_email(request, user, account_type)

    # if pro, then mentor IS mentor
    if account_type == 1:
      try:
        mentor = User.objects.get(email=form.cleaned_data['mentor'], groups__in=[pro_group])
      except User.DoesNotExist:
        # mentor e-mail was not entered, assign default pro
        mentor = get_default_pro()

      profile.mentor = mentor
      ProSignupLog.objects.get_or_create(new_pro=user, mentor=mentor, mentor_email=form.cleaned_data['mentor'])
      profile.save()
      send_pro_request_email(request, user)
    elif account_type == 2:
      # if host, then set mentor to be the host's pro
      # host does not get assigned to anybody if they don't enter pro e-mail 3/10/2013
      try:
        pro = User.objects.get(email=form.cleaned_data['mentor'], groups__in=[pro_group])
        profile.current_pro = pro
        send_know_pro_party_email(request, user)  # to host
      except User.DoesNotExist:
        pro = None
        # pro e-mail was not entered
        # profile.current_pro = profile.find_nearest_pro()
        send_unknown_pro_email(request, user)  # to host
      profile.save()
      send_host_vinely_party_email(request, user, pro)  # to pro or vinely

    if role == pro_group:
      # if requesting to be pro, put them in pending pro group
      user.groups.add(pro_pending_group)
    else:
      user.groups.add(role)

    # save engagement type
    interest, created = EngagementInterest.objects.get_or_create(user=user, engagement_type=account_type)

    data["email"] = user.email
    data["first_name"] = user.first_name

    data["account_type"] = account_type

    messages.success(request, "To ensure that Vinely emails get to your inbox, please add info@vinely.com to your email Address Book or Safe List.")
    user = authenticate(email=user.email, password=form.cleaned_data['password1'])
    if user is not None:
      login(request, user)
      success_url = request.GET.get('next') if request.GET.get('next') else reverse('home_page')
    return HttpResponseRedirect(success_url)

  data['form'] = form
  data['role'] = role.name
  data['account_type'] = account_type
  # data['get_started_menu'] = True

  return render_to_response("accounts/make_host_pro_signup.html", data, context_instance=RequestContext(request))


def sign_up_old(request, account_type):
  """
    :param account_type: 1 - Vinely Pro
                          2 - Vinely Host
                          3 - Vinely Taster
                          4 - Supplier
                          5 - Vinely Tasting Lead
  """

  data = {}
  role = None

  account_type = int(account_type)

  pro_group = Group.objects.get(name="Vinely Pro")
  hos_group = Group.objects.get(name="Vinely Host")
  tas_group = Group.objects.get(name="Vinely Taster")
  pro_pending_group = Group.objects.get(name="Pending Vinely Pro")

  ### Handle people who are signing up fresh
  if account_type in [3, 5]:
    # people who order wine tasting kit
    role = tas_group
  elif account_type == 1:
    role = pro_group
  elif account_type == 2:
    role = hos_group

  if not role:
    # currently suppliers cannot sign up
    raise Http404

  # create users and send e-mail notifications
  form = NameEmailUserMentorCreationForm(request.POST or None, initial={'account_type': account_type})

  if form.is_valid():
    user = form.save()
    profile = user.get_profile()
    profile.zipcode = form.cleaned_data['zipcode']
    profile.phone = form.cleaned_data['phone_number']
    ok = check_zipcode(profile.zipcode)

    if not ok:
      messages.info(request, 'Please note that Vinely does not currently operate in your area.')
      send_not_in_area_party_email(request, user, account_type)

    # if pro, then mentor IS mentor
    if account_type == 1:
      try:
        pro = User.objects.get(email=form.cleaned_data['mentor'], groups__in=[pro_group])
        profile.mentor = pro
        ProSignupLog.objects.get_or_create(new_pro=user, mentor=pro, mentor_email=form.cleaned_data['mentor'])
      except User.DoesNotExist:
        # mentor e-mail was not entered
        ProSignupLog.objects.get_or_create(new_pro=user, mentor=None, mentor_email=form.cleaned_data['mentor'])

    elif account_type == 2:
      # if host, then set mentor to be the host's pro
      try:
        pro = User.objects.get(email=form.cleaned_data['mentor'], groups__in=[pro_group])
          # map host to a pro
        my_hosts, created = MyHost.objects.get_or_create(pro=pro, host=user)
      except User.DoesNotExist:
        # pro e-mail was not entered
        my_hosts, created = MyHost.objects.get_or_create(pro=None, host=user, email_entered=form.cleaned_data['mentor'])

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
        mentor_pro = User.objects.get(email=request.POST.get('mentor'))

        if pro_group in mentor_pro.groups.all():
          send_know_pro_party_email(request, user)  # to host
      except User.DoesNotExist, e:
        # mail sales
        send_unknown_pro_email(request, user)  # to host

      send_host_vinely_party_email(request, user, mentor_pro)  # to pro or vinely
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

    messages.success(request, "Your new e-mail %s has been verified and old e-mail %s removed." % (user.email, old_email))

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
  u = request.user

  try:
    verification = VerificationQueue.objects.get(verification_code=verification_code)
    if verification.verified:
      # data["error"] = "You have already been verified"
      messages.success(request, "You have already been verified.")
      return HttpResponseRedirect(reverse("home_page"))
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
      # profile.accepted_tos = True
      profile.save()

      user = authenticate(email=user.email, password=form.cleaned_data['new_password'])
      if user is not None:
        login(request, user)
      else:
        log.debug("For some reason %s could not be verified and authenticated." % user.email)
        return HttpResponseRedirect(reverse("login"))

      if verification.verification_type == VerificationQueue.VERIFICATION_CHOICES[0][0]:
        messages.success(request, "Your account has been verified and now is active.")
      elif verification.verification_type == VerificationQueue.VERIFICATION_CHOICES[1][0]:
        messages.success(request, "Your password has been reset to your new password.")

      # if user is taster and was invited to a party, redirect them to RSVP page
      invites = PartyInvite.objects.filter(invitee=u, response=0, party__event_date__gte=timezone.now()).order_by('party__event_date')
      if invites.exists():
        return HttpResponseRedirect(reverse('party_rsvp', args=[invites[0].party.id]))

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
def pro_link(request):
  u = request.user
  profile = u.get_profile()

  if profile.is_host() or profile.is_taster():
    form = ProLinkForm(request.POST or None)
    if form.is_valid():
      pro = User.objects.get(email=form.cleaned_data['email'])
      my_hosts, created = MyHost.objects.get_or_create(pro=pro, host=u)
      profile.current_pro = pro
      profile.mentor = None
      profile.save()
      messages.success(request, "You were successfully linked to the pro %s." % pro.email)
    if form.errors:
      messages.error(request, form.errors)
  else:
    # TODO: Can tasters link to particular pros?
    messages.error(request, "Only Hosts and Tasters can link to Pro's at the moment")
  return HttpResponseRedirect(reverse('edit_subscription'))


@login_required
def pro_unlink(request):

  u = request.user
  profile = u.get_profile()

  # unlink current user's pro
  if profile.is_host():
    profile.mentor = None  # this line shouldn't be necessary with new way of tracking pros 3/10/2013
    profile.current_pro = None
    profile.save()
    MyHost.objects.filter(host=u).update(pro=None)
    messages.success(request, "You have been successfully unlinked from the Pro.")
  elif profile.is_taster():
    profile.mentor = None  # this line shouldn't be necessary with new way of tracking pros 3/10/2013
    profile.current_pro = None
    profile.save()
    # seems there's no way to unlink a pro for taster because no direct link
    messages.success(request, "You have been successfully unlinked from the Pro.")

  return HttpResponseRedirect(reverse("edit_subscription"))


def join_club(request, state=None):
  data = {}
  form = NameEmailUserMentorCreationForm(request.POST or None, initial={'account_type': 3})
  # eligibility_form = AgeValidityForm(request.POST or None, prefix='eligibility')
  login_form = VinelyEmailAuthenticationForm(request.POST or None)
  data['form'] = form
  # data['eligibility_form'] = eligibility_form
  data['login_form'] = login_form
  return render_to_response("accounts/join_club.html", data, context_instance=RequestContext(request))
