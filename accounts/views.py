# Create your views here.
from urlparse import urlparse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from emailusernames.forms import EmailAuthenticationForm

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

  return render_to_response("accounts/settings.html", data, 
                        context_instance=RequestContext(request))

