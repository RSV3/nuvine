# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required

from django.conf import settings
import stripe

