from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404

from emailusernames.forms import EmailAuthenticationForm

from cms.models import ContentTemplate


def home(request):
  """

  """
  data = {}
  u = request.user

  form = EmailAuthenticationForm()
  form.fields['email'].widget.attrs['placeholder'] = 'E-mail'
  form.fields['password'].widget.attrs['placeholder'] = 'Password'
  data['form'] = form
  data['general_section'] = ContentTemplate.objects.get(key='landing_page').sections.all()[0].content
  if u.is_authenticated():
    if u.userprofile.is_supplier():
      return HttpResponseRedirect(reverse("supplier_all_orders"))
    else:
      return HttpResponseRedirect(reverse("home_page"))

  return render_to_response("winedora/home.html", data, context_instance=RequestContext(request))


def tos(request):
  """
    Terms of service
  """
  data = {}

  return render_to_response("winedora/tos.html", data, context_instance=RequestContext(request))


def pinterest(request):
  """
    Pinterest verification
  """
  data = {}
  return render_to_response("pinterest-868f3.html", data, context_instance=RequestContext(request))
