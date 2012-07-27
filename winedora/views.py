from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404


def home(request):
  """

  """
  data = {}

  if request.user.is_authenticated():
    return HttpResponseRedirect(reverse("home_page"))

  return render_to_response("winedora/home.html", data, context_instance=RequestContext(request))


