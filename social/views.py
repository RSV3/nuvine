# Create your views here.
from social import xoauth
from django.http import HttpResponse 

def get_xoauth_gmail( request ):

  if request.method == "POST":
    user_email = request.POST.get('user') 
    oauth_token = request.POST.get('token')
    oauth_secret = request.POST.get('secret')

    if user_email is None:
      return HttpResponse("Missing user parameter")
    if oauth_token is None: 
      return HttpResponse("Missing token parameter")
    if oauth_secret is None:
      return HttpResponse("Missing secret parameter")

    xoauth_token = xoauth.get_xoauth_token_min( user_email, oauth_token, oauth_secret )
    return HttpResponse(xoauth_token)
  else:
    return HttpResponse("Please POST")
