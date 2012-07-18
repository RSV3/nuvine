# Create your views here.
from urlparse import urlparse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

from main.models import Party, PartyInvite
from personality.models import Wine 

from main.forms import ContactRequestForm, PartyCreateForm, PartyInviteAttendeeForm, PartySpecialistSignupForm
from personality.forms import WineRatingsForm, AllWineRatingsForm

from personality.utils import calculate_wine_personality

import json

from datetime import date

@login_required
def home(request):
  data = {}

  u = request.user

  if request.user.is_authenticated():
    data["output"] = "User is authenticated"

    ps_group = Group.objects.get(name='Party Specialist')
    ph_group = Group.objects.get(name='Party Host')
    sp_group = Group.objects.get(name='Supplier')
    at_group = Group.objects.get(name='Attendee')

    if ps_group in u.groups.all():
      data["specialist"] = True
    if ph_group in u.groups.all():
      data["host"] = True
    if sp_group in u.groups.all():
      data["supplier"] = True
    if at_group in u.groups.all():
      data["attendee"] = True

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
      return render_to_response("main/thankyou_contact.html", data, context_instance=RequestContext(request))
  else:
    form = ContactRequestForm()

  data["form"] = form

  return render_to_response("main/contact_us.html", data, context_instance=RequestContext(request))

@login_required
def start_order(request):
  """
    Show order page
  
    Add items to cart and go to cart view 
  """
  data = {}

  return render_to_response("main/start_order.html", data, context_instance=RequestContext(request))

@login_required
def cart(request):
  """
    
    Show items in cart, have a link to go back to start_order to order more

    submit goes to checkout
  """
  data = {}

  return render_to_response("main/cart.html", data, context_instance=RequestContext(request))

@login_required
def checkout(request):
  """
    Fill out credit card, shipping and billing address

    Submit will lead to main/order_complete.html
  """
  data = {}
  return render_to_response("main/checkout.html", data, context_instance=RequestContext(request))

@login_required
def view_orders(request):
  data = {}
  return render_to_response("main/view_orders.html", data, context_instance=RequestContext(request))

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
def record_all_wine_ratings(request, email=None):
  """
    Record wine ratings.
    Used by party specialists or attendees themselves.

  """

  #TODO: Need to track the party specialist that is adding the ratings so that this attendee is linked
  #     to the party specialist

  data = {}

  u = request.user

  ps_group = Group.objects.get(name="Party Specialist")
  ph_group = Group.objects.get(name="Party Host")
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
         
        if (ps_group in u.groups.all()) or (ps_group in u.groups.all()):
          # ask if you want to fill out next customer's ratings or order wine
          data["role"] = "specialist"
        elif (att_group in u.groups.all()):
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

      if email:
        attendee = User.objects.get(email=email)
        initial_data['email'] = attendee.email
        initial_data['first_name'] = attendee.first_name
        initial_data['last_name'] = attendee.last_name

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

def signup_party_specialist(request):

  data = {}
  
  form = PartySpecialistSignupForm(request.POST or None)

  data["form"] = form

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

  u = request.user

  data = {}

  ps_group = Group.objects.get(name="Party Specialist")
  ph_group = Group.objects.get(name="Party Host")

  if (ps_group in u.groups.all()):
    # TODO: need to filter to parties that a particular user manages
    my_hosts = MyHosts.objects.filter(specialist=u).values_list('host', flat=True)
    data['parties'] = Party.objects.filter(host__in=my_hosts)
  elif (ph_group in u.groups.all()):
    data['parties'] = Party.objects.filter(host=u)
  else:
    raise Http404

  return render_to_response("main/party_list.html", data, context_instance=RequestContext(request))

@login_required
def party_add(request):
  """
    Add a new party
  """
  data = {}

  u = request.user

  if request.method == "POST":
    form = PartyCreateForm(request.POST)
    if form.is_valid():

      new_party = form.save()
      new_host = new_party.host

      if not new_host.is_active:

        # map host to a specialist
        my_hosts = MyHosts(specialist=u, host=new_host)
        my_hosts.save()

        # new host, so send password and invitation
        temp_password = User.objects.make_random_password()
        new_host.set_password(temp_password)
        new_host.save()

        verification_code = str(uuid.uuid4())
        vque = VerificationQueue(user=new_host, verification_code=verification_code)
        vque.save()

        # send an invitation e-mail if new user created 
        send_new_invitation_email(request, verification_code, temp_password, new_host.email)

      # go to party list page
      return HttpResponseRedirect(reverse("party_list"))
  else:
    initial_data = {'event_date': date.today().strftime("%m/%d/%Y")}
    form = PartyCreateForm(initial=initial_data)

  data["form"] = form

  return render_to_response("main/party_add.html", data, context_instance=RequestContext(request))

@login_required
def party_attendee_list(request, party_id):
  """
    Show attendees of a party
  """

  data = {}

  u = request.user

  party = None
  if int(party_id) != 0:
    party = get_object_or_404(Party, pk=party_id)

  ps_group = Group.objects.get(name='Party Specialist')
  ph_group = Group.objects.get(name='Party Host')
  sp_group = Group.objects.get(name='Supplier')
  if ps_group in u.groups.all() or ph_group in u.groups.all() or sp_group in u.groups.all(): 
    
    invitees = PartyInvite.objects.filter(party=party)

    data["party"] = party
    data["invitees"] = invitees

    return render_to_response("main/party_attendee_list.html", data, context_instance=RequestContext(request))
  else:
    raise Http404

@login_required
def party_attendee_invite(request, party_id=0):
  """
    Invite a new attendee to a party 

      - only allow host or party specialist to add
      - need to track who added and make sure the attendee is linked to that specialist or host

  """
  data = {}



  u = request.user

  party = None
  if int(party_id) != 0:
    party = get_object_or_404(Party, pk=party_id)

  ps_group = Group.objects.get(name='Party Specialist')
  ph_group = Group.objects.get(name='Party Host')
  if ps_group in u.groups.all() or ph_group in u.groups.all(): 
    if request.method == "POST":
      form = PartyInviteAttendeeForm(request.POST)
      if form.is_valid():
        new_invite = form.save()

        new_invitee = new_invite.invitee
        if not new_invitee.is_active:
          # new user created through party invitation
          temp_password = User.objects.make_random_password()
          new_invitee.set_password(temp_password)
          new_invitee.save()

          verification_code = str(uuid.uuid4())
          vque = VerificationQueue(user=new_invitee, verification_code=verification_code)
          vque.save()

          # send an invitation e-mail if new user created 
          send_new_invitation_email(request, verification_code, temp_password, new_invitee.email)

        return HttpResponseRedirect(reverse("party_attendee_list", args=[new_invite.party.id]))
    else:
      if int(party_id) == 0:
        form = PartyInviteAttendeeForm()
      else:
        initial_data = {'party': party}
        form =  PartyInviteAttendeeForm(initial=initial_data)

    data["form"] = form
    data["party"] = party

    return render_to_response("main/party_attendee_invite.html", data, context_instance=RequestContext(request))
  else:
    raise Http404

@login_required
def supplier_party_list(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
def party_order_list(request, party_id):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
def pending_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
def fulfilled_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
def all_orders(request):
  """
    Shows party list from suppliers point of view

    So it displays all parties
  """
  data = {}

  data['parties'] = Party.objects.all()

  return render_to_response("main/supplier_party_list.html", data, context_instance=RequestContext(request))

@login_required
def edit_subscription(request):
  """
    Update one's subscription's

    - Cancel
    - Change product
    - Change frequency
  """
  data = {}

  return render_to_response("main/edit_subscription.html", data, context_instance=RequestContext(request))

