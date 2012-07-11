# Create your views here.
from urlparse import urlparse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

@login_required
def my_wine_personality(request):
  data = {}

  u = request.user

  data["personality"] = u.get_profile().wine_personality

  return render_to_response("personality/my_wine_personality.html", data, context_instance=RequestContext(request))

