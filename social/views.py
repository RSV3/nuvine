# Create your views here.
from social import xoauth
from social.forms import XOAuthForm
from django.http import HttpResponse 
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_xoauth_gmail( request ):

  form = XOAuthForm(request.POST or None)
  if form.is_valid():
    user_email = form.cleaned_data['user'].encode('ascii')
    oauth_token = form.cleaned_data['token'].encode('ascii')
    oauth_secret = form.cleaned_data['secret'].encode('ascii')

    if user_email is None:
      return HttpResponse("Missing user parameter")
    if oauth_token is None: 
      return HttpResponse("Missing token parameter")
    if oauth_secret is None:
      return HttpResponse("Missing secret parameter")

    xoauth_token = xoauth.get_xoauth_token_min( user_email, oauth_token, oauth_secret )
    return HttpResponse(xoauth_token)
  else:
    return HttpResponse("Form parameters are not valid.")

  return HttpResponse("Please POST")
