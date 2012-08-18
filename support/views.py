from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from support.models import Email

@staff_member_required
def list_emails(request):

  data = {}

  emails = Email.objects.all()

  data["emails"] = emails

  return render_to_response("support/list_emails.html", data, context_instance=RequestContext(request))

@staff_member_required
def view_email(request, email_id):

  email = get_object_or_404(Email, pk=email_id)

  return HttpResponse(email.html) 
