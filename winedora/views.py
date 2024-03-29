from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from emailusernames.forms import EmailAuthenticationForm
from django.utils import timezone

from main.models import Party
from cms.models import ContentTemplate


def home(request):
  """

  """
  data = {}
  u = request.user
  data['title'] = 'Change the way you experience wine'
  form = EmailAuthenticationForm()
  form.fields['email'].widget.attrs['placeholder'] = 'E-mail'
  form.fields['password'].widget.attrs['placeholder'] = 'Password'
  data['form'] = form
  sections = ContentTemplate.objects.get(key='landing_page').sections
  data['header'] = sections.get(key='header').content
  data['overview_col1'] = sections.get(key='overview_col1').content
  data['overview_col2'] = sections.get(key='overview_col2').content
  data['host'] = sections.get(key='host').content
  data['pro'] = sections.get(key='pro').content

  if u.is_authenticated():
    profile = u.get_profile()
    if profile.is_supplier():
      return HttpResponseRedirect(reverse("supplier_all_orders"))
    elif profile.is_taster():
      if profile.club_member:
        return HttpResponseRedirect(reverse("home_club_member"))
      else:
        return HttpResponseRedirect(reverse("home_page"))
    elif profile.is_host():
      parties = Party.objects.filter(host=u, event_date__gt=timezone.now())
      if parties.exists():
        return HttpResponseRedirect(reverse('home_page'))
      elif profile.club_member:
        return HttpResponseRedirect(reverse('home_club_member'))
      else:
        return HttpResponseRedirect(reverse('home_page'))
    else:
      return HttpResponseRedirect(reverse('home_page'))

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
