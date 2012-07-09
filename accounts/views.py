# Create your views here.
from urlparse import urlparse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from emailusernames.forms import EmailAuthenticationForm, EmailUserCreationForm

@login_required
def profile(request):
  """
    After user logged in
  """
  return HttpResponseRedirect(reverse('home_page'))

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

  if request.method == 'POST':
    # create users and send e-mail notifications
    form = EmailUserCreationForm(request.POST) 

    if form.is_valid():
      user = form.save()

      if int(account_type) == 0:
        user.groups.add(Group.objects.get(name="Party Specialist"))
      elif int(account_type) == 2:
        user.groups.add(Group.objects.get(name="Party Host"))
      elif int(account_type) == 3:
        user.groups.add(Group.objects.get(name="Party Attendee"))
      elif int(account_type) == 4:
        user.groups.add(Group.objects.get(name="Party Supplier"))

      user.is_active = False
      user.save()

      # TODO: send out verification e-mail
  else:
    form = EmailUserCreationForm()
    # show forms

  data['form'] = form

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

  if request.method == 'POST':
    form = VerifyAccountForm(request.POST)
    if form.is_valid():
      form.save()
      # activate user
      user = verify.user
      user.is_active = True
      user.save()
  else:
    form = VerifyAccountForm()

  data["form"] = form

  verify = VerificationQueue.objects.get(verification_code=verfication_code)
  data["email"] = verify.user.email

  verify.delete()

  return render_to_response("accounts/verify_account.html", data,
                        context_instance=RequestContext(request))