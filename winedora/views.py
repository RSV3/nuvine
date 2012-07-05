from django.shortcuts import render_to_response
from django.template import RequestContext


def home(request):
  """

  """
  data = {}

  return render_to_response("winedora/home.html", data, context_instance=RequestContext(request))


