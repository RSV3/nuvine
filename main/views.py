# Create your views here.
from urlparse import urlparse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from personality.models import Wine 

from main.forms import ContactRequestForm
from personality.forms import WineRatingsForm, AllWineRatingsForm
from personality.utils import calculate_wine_personality

import json

@login_required
def home(request):
  data = {}

  u = request.user

  if request.user.is_authenticated():
    data["output"] = "User is authenticated"

    # go to home page

    # if user is party specialist
    # - be able to add new users and send them e-mail 
    # - see users registered at a party
    # - add a new host
    # - be able to order for a user
    # - be able to enter ratings for a user

    # if user is host
    # - list of parties (aggregate view of orders placed)
    # - list of attendees in each party (aggregate of what each attendee ordered)
    # - see orders placed by each attendee in detail 
    # - create party
    # - invite attendees

    # if user is attendee
    # - my wine personality
    # - order wine

    # if user is admin
    pass
  else:
    data["output"] = "User is not authenticated"
    return HttpResponseRedirect(reverse("landing_page"))

  return render_to_response("main/home.html", data, context_instance=RequestContext(request))

def about(request):
  """

  """

  data = {}

  return render_to_response("main/about.html", data, context_instance=RequestContext(request))

def contact_us(request):
  """

  """

  data = {}

  if request.method == "POST":
    form = ContactRequestForm(request.POST)
    if form.is_valid():
      form.save()
      # TODO: alert saying
      form = ContactRequestForm() 
  else:
    form = ContactRequestForm()

  data["form"] = form

  return render_to_response("main/contact_us.html", data, context_instance=RequestContext(request))

@login_required
def start_order(request):
  """
    Show order page
  
  """
  data = {}

  return render_to_response("main/start_order.html", data, context_instance=RequestContext(request))

@login_required
def record_wine_ratings(request):
  """
    Record wine ratings for a particular wine.
    Used by party specialists or attendees themselves.
  """

  data = {}

  u = request.user

  ps_group = Group.objects.get(name="Party Specialist")
  att_group = Group.objects.get(name="Attendee")

  if (ps_group in u.groups.all()) or (att_group in u.groups.all()):
    # one can record ratings only if party specialist or attendee

    if request.method == "POST":
      form = WineRatingsForm(request.POST)
      if form.is_valid():
        form.save()      

        if (ps_group in u.groups.all()):
          # ask if you want to fill out next customer's ratings or order wine
          data["role"] = "specialist"
          
        if (att_group in u.groups.all()):
          # ask if you want order wine
          data["role"] = "attendee"

        return render_to_response("main/ratings_saved.html", data, context_instance=RequestContext(request))
    else:
      # show forms
      form = WineRatingsForm()

    data["form"] = form

    return render_to_response("main/record_wine_ratings.html", data, context_instance=RequestContext(request))
  else:
    raise Http404 

@login_required
def record_all_wine_ratings(request):
  """
    Record wine ratings.
    Used by party specialists or attendees themselves.

  """

  #TODO: Need to track the party specialist that is adding the ratings so that this attendee is linked
  #     to the party specialist

  data = {}

  u = request.user

  ps_group = Group.objects.get(name="Party Specialist")
  att_group = Group.objects.get(name="Attendee")

  if (ps_group in u.groups.all()) or (att_group in u.groups.all()):
    # one can record ratings only if party specialist or attendee

    if request.method == "POST":
      form = AllWineRatingsForm(request.POST)
      if form.is_valid():
        results = form.save() 
        data["invitee"] = results[0]

        personality = calculate_wine_personality(*results)
        data["personality"] = personality

        if (ps_group in u.groups.all()):
          # ask if you want to fill out next customer's ratings or order wine
          data["role"] = "specialist"
          
        if (att_group in u.groups.all()):
          # ask if you want order wine
          data["role"] = "attendee"

        return render_to_response("main/ratings_saved.html", data, context_instance=RequestContext(request))

    else:
      # show forms
      initial_data = { 'wine1': Wine.objects.get(number=1, active=True).id,
                        'wine2': Wine.objects.get(number=2, active=True).id,
                        'wine3': Wine.objects.get(number=3, active=True).id,
                        'wine4': Wine.objects.get(number=4, active=True).id,
                        'wine5': Wine.objects.get(number=5, active=True).id,
                        'wine6': Wine.objects.get(number=6, active=True).id
                        }

      form = AllWineRatingsForm(initial=initial_data)

    data["form"] = form

    return render_to_response("main/record_all_wine_ratings.html", data, context_instance=RequestContext(request))

  else:
    # user needs to be a party specialist or attendee to fill this out
    # attendee is filling out their own data
    raise Http404 

@login_required
def parties(request):
  """
    Show list of parties
  """
  data = {}

  data["parties"] = Party.objects.all()
  data["party_invites"] = PartyInvite.objects.values('party').annotate(num_invites=Count('invitee'))

  return render_to_response("main/parties.html", data, context_instance=RequestContext(request))

@login_required
def add_invitees(request):
  """
    Add invitees 
  """

  data = {}

  u = request.user

  return render_to_response("main/add_invitees.html", data, context_instance=RequestContext(request))

def signup_party_specialist(request):

  data = {}

  return render_to_response("main/signup_party_specialist.html", data, context_instance=RequestContext(request))

def signup_party_attendee(request):

  data = {}

  return render_to_response("main/signup_party_attendee.html", data, context_instance=RequestContext(request))

def signup_party_host(request):

  data = {}

  return render_to_response("main/signup_party_host.html", data, context_instance=RequestContext(request))

@login_required
def tag(request):
  """ 
    Tag a member with particular term 
    - people can edit tags 
    - ajax call
    - log those people who added those tags
  """
  data = {}

  data["result"] = "tagging successful"

  return HttpResponse(json.dumps(data), mimetype="application/json") 


@login_required
def party_list(request):
  data = {}

  return render_to_response("main/party_list.html", data, context_instance=RequestContext(request))

@login_required
def party_add(request):
  """
    Add a new party
  """
  data = {}

  return render_to_response("main/party_add.html", data, context_instance=RequestContext(request))

@login_required
def party_attendee_add(request):
  """
    Add a new attendee to a party 
  """
  data = {}

  # TODO: only allow host or party specialist to add

  # TODO: need to track who added and make sure the attendee is linked to that specialist or host

  return render_to_response("main/party_attendee_add.html", data, context_instance=RequestContext(request))



