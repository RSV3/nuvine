# Create your views here.`
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from main.utils import if_supplier
from personality.models import Wine, WineRatingData, GeneralTaste, WineTaste, WinePersonality
from main.models import Order, Party, PersonaLog, PartyInvite, OrganizedParty
from accounts.models import VerificationQueue
from personality.forms import GeneralTasteQuestionnaire, WineTasteQuestionnaire, WineRatingsForm, AllWineRatingsForm, \
                              AddTasterRatingsForm

from personality.utils import calculate_wine_personality
from accounts.utils import send_verification_email

import numpy as np
import uuid, json, re


@login_required
def check_personality_exists(request):
  data = {}

  data["result"] = 0
  email = request.POST.get('email', None)
  if email:
    email = email.lower()
    email_re = re.compile("^[_A-Za-z0-9-]+(\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$", flags=re.IGNORECASE)
    if email_re.search(email):
      try:
        guest = User.objects.get(email=email)
        mystery = WinePersonality.objects.get(name=WinePersonality.MYSTERY)
        if guest.get_profile().wine_personality != mystery:
          data["result"] = 1
          return HttpResponse(json.dumps(data), mimetype="application/json")
      except User.DoesNotExist:
        pass
    else:
      # invalid e-mail
      data["result"] = -1
      return HttpResponse(json.dumps(data), mimetype="application/json")

  return HttpResponse(json.dumps(data), mimetype="application/json")


@login_required
def my_wine_personality(request):
  data = {}

  u = request.user

  data["personality"] = u.get_profile().wine_personality

  return render_to_response("personality/my_wine_personality.html", data, context_instance=RequestContext(request))


@login_required
@user_passes_test(if_supplier, login_url="/suppliers/only/")
def personality_details(request, user_id, order_id=None):
  data = {}

  u = request.user

  receiver = get_object_or_404(User, pk=user_id)

  if order_id:
    order = get_object_or_404(Order, order_id=order_id)
    data["order"] = order

  data["personality"] = receiver.get_profile().wine_personality

  rating_data = {}

  try:
    rating_data['wine1'] = WineRatingData.objects.get(user__id=user_id, wine__id=1)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine2'] = WineRatingData.objects.get(user__id=user_id, wine__id=2)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine3'] = WineRatingData.objects.get(user__id=user_id, wine__id=3)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine4'] = WineRatingData.objects.get(user__id=user_id, wine__id=4)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine5'] = WineRatingData.objects.get(user__id=user_id, wine__id=5)
  except WineRatingData.DoesNotExist:
    pass
  try:
    rating_data['wine6'] = WineRatingData.objects.get(user__id=user_id, wine__id=6)
  except WineRatingData.DoesNotExist:
    pass

  data["rating_data"] = rating_data

  return render_to_response("personality/personality_details.html", data, context_instance=RequestContext(request))


@login_required
def pre_questionnaire_general(request):
  data = {}

  u = request.user

  try:
    general_taste = GeneralTaste.objects.get(user=u)
  except GeneralTaste.DoesNotExist:
    general_taste = None

  form = GeneralTasteQuestionnaire(request.POST or None, instance=general_taste)
  if form.is_valid():
    form.save()
    messages.success(request, "Your general taste information has been saved.")
    return HttpResponseRedirect(reverse("pre_questionnaire_wine"))

  if general_taste is None:
    form.initial['user'] = u
  data["form"] = form

  return render_to_response("personality/pre_questionnaire_general.html", data,
                                  context_instance=RequestContext(request))


@login_required
def pre_questionnaire_wine(request):
  data = {}

  u = request.user
  profile = u.get_profile()

  try:
    wine_taste = WineTaste.objects.get(user=u)
  except WineTaste.DoesNotExist:
    wine_taste = None

  form = WineTasteQuestionnaire(request.POST or None, instance=wine_taste)
  if form.is_valid():
    form.save()
    # save information that questionnaire has been filled out
    if GeneralTaste.objects.filter(user=u).exists():
      profile.prequestionnaire = True
      profile.save()
    messages.success(request, "Your wine taste information has been saved.")
    return HttpResponseRedirect(reverse("home_page"))

  if wine_taste is None:
    form.initial['user'] = u
  data["form"] = form

  return render_to_response("personality/pre_questionnaire_wine.html", data,
                                  context_instance=RequestContext(request))


@login_required
def record_wine_ratings(request):
  """
    Record wine ratings for a particular wine.
    Used by Vinely Pros or Vinely Tasters themselves.
  """

  data = {}

  u = request.user

  pro_group = Group.objects.get(name="Vinely Pro")
  tas_group = Group.objects.get(name="Vinely Taster")

  if (pro_group in u.groups.all()) or (tas_group in u.groups.all()):
    # one can record ratings only if Vinely Pro or Vinely Taster

    if request.method == "POST":
      form = WineRatingsForm(request.POST)
      if form.is_valid():
        form.save()

        if (pro_group in u.groups.all()):
          # ask if you want to fill out next customer's ratings or order wine
          data["role"] = "pro"

        if (tas_group in u.groups.all()):
          # ask if you want order wine
          data["role"] = "taster"

        return render_to_response("personality/ratings_saved.html", data, context_instance=RequestContext(request))
    else:
      # show forms
      form = WineRatingsForm()

    data["form"] = form

    return render_to_response("personality/record_wine_ratings.html", data, context_instance=RequestContext(request))
  else:
    raise Http404


@login_required
def record_ratings(request, email=None, party_id=None):
  """

  """

  data = {}
  return render_to_response("personality/record_all_wine_ratings.html", data, context_instance=RequestContext(request))


@login_required
def personality_rating_info(request, email=None, party_id=None):
  return record_all_wine_ratings(request, email, party_id, None)


@login_required
def record_all_wine_ratings(request, email=None, party_id=None, rate=1):
  """
    Record wine ratings.
    Used by Vinely Pros or Vinely Tasters themselves.

  """

  #TODO: Need to track the Vinely Pro that is adding the ratings so that this Vinely Taster is linked
  #     to the Vinely Pro

  data = {}

  u = request.user

  party = None

  party = get_object_or_404(Party, pk=party_id)
  
  # used in ratings_saved.html template to go back to party details
  data["party_id"] = party_id
  data["party"] = party

  pro_group = Group.objects.get(name="Vinely Pro")
  hos_group = Group.objects.get(name="Vinely Host")
  tas_group = Group.objects.get(name="Vinely Taster")
  if pro_group in u.groups.all():
    data["pro"] = True
  if hos_group in u.groups.all():
    data["host"] = True
  if tas_group in u.groups.all():
    data["taster"] = True

  if u.get_profile().is_pro():
    try:
      OrganizedParty.objects.get(party=party, pro=u)
    except OrganizedParty.DoesNotExist:
      messages.error(request, 'You can only add ratings for your own parties')
      return HttpResponseRedirect(reverse('party_list'))

  if (pro_group in u.groups.all()) or (tas_group in u.groups.all()) or (hos_group in u.groups.all()):
    # one can record ratings only if Vinely Pro or Vinely Host/Vinely Taster

    if email:
      email = email.lower()

      # if not the pro then must have been invited to the party
      try:
        taster = User.objects.get(email=email)
        if u.email != email:  # True for the pro
          if party.host.email == email:
            taster = party.host
          else:
            invite = PartyInvite.objects.get(invitee=taster, party=party)
      except (User.DoesNotExist, PartyInvite.DoesNotExist):
          messages.error(request, "(%s) is not an invitee to the party. They must be added as tasters first to enter their ratings." % email)
          return HttpResponseRedirect(reverse('party_list'))
    else:
      # enter your own information
      taster = u

    data['personality_exists'] = taster.get_profile().has_personality()
    data['invitee'] = taster

    # show forms
    wine1 = Wine.objects.get(number=1, active=True)
    wine2 = Wine.objects.get(number=2, active=True)
    wine3 = Wine.objects.get(number=3, active=True)
    wine4 = Wine.objects.get(number=4, active=True)
    wine5 = Wine.objects.get(number=5, active=True)
    wine6 = Wine.objects.get(number=6, active=True)

    initial_data = { 'wine1': wine1.id,
                      'wine2': wine2.id,
                      'wine3': wine3.id,
                      'wine4': wine4.id,
                      'wine5': wine5.id,
                      'wine6': wine6.id
                      }

    if taster:
      initial_data['email'] = taster.email

      try:
        wine1_rating = WineRatingData.objects.get(user=taster, wine=wine1)
        initial_data['wine1_overall'] = wine1_rating.overall
        initial_data['wine1_sweet'] = wine1_rating.sweet
        initial_data['wine1_sweet_dnl'] = wine1_rating.sweet_dnl
        initial_data['wine1_weight'] = wine1_rating.weight
        initial_data['wine1_weight_dnl'] = wine1_rating.weight_dnl
        initial_data['wine1_texture'] = wine1_rating.texture
        initial_data['wine1_texture_dnl'] = wine1_rating.texture_dnl
        initial_data['wine1_sizzle'] = wine1_rating.sizzle
        initial_data['wine1_sizzle_dnl'] = wine1_rating.sizzle_dnl
      except WineRatingData.DoesNotExist:
        pass

      try:
        wine2_rating = WineRatingData.objects.get(user=taster, wine=wine2)
        initial_data['wine2_overall'] = wine2_rating.overall
        initial_data['wine2_sweet'] = wine2_rating.sweet
        initial_data['wine2_sweet_dnl'] = wine2_rating.sweet_dnl
        initial_data['wine2_weight'] = wine2_rating.weight
        initial_data['wine2_weight_dnl'] = wine2_rating.weight_dnl
        initial_data['wine2_texture'] = wine2_rating.texture
        initial_data['wine2_texture_dnl'] = wine2_rating.texture_dnl
        initial_data['wine2_sizzle'] = wine2_rating.sizzle
        initial_data['wine2_sizzle_dnl'] = wine2_rating.sizzle_dnl
      except WineRatingData.DoesNotExist:
        pass

      try:
        wine3_rating = WineRatingData.objects.get(user=taster, wine=wine3)
        initial_data['wine3_overall'] = wine3_rating.overall
        initial_data['wine3_sweet'] = wine3_rating.sweet
        initial_data['wine3_sweet_dnl'] = wine3_rating.sweet_dnl
        initial_data['wine3_weight'] = wine3_rating.weight
        initial_data['wine3_weight_dnl'] = wine3_rating.weight_dnl
        initial_data['wine3_texture'] = wine3_rating.texture
        initial_data['wine3_texture_dnl'] = wine3_rating.texture_dnl
        initial_data['wine3_sizzle'] = wine3_rating.sizzle
        initial_data['wine3_sizzle_dnl'] = wine3_rating.sizzle_dnl
      except WineRatingData.DoesNotExist:
        pass

      try:
        wine4_rating = WineRatingData.objects.get(user=taster, wine=wine4)
        initial_data['wine4_overall'] = wine4_rating.overall
        initial_data['wine4_sweet'] = wine4_rating.sweet
        initial_data['wine4_sweet_dnl'] = wine4_rating.sweet_dnl
        initial_data['wine4_weight'] = wine4_rating.weight
        initial_data['wine4_weight_dnl'] = wine4_rating.weight_dnl
        initial_data['wine4_texture'] = wine4_rating.texture
        initial_data['wine4_texture_dnl'] = wine4_rating.texture_dnl
        initial_data['wine4_sizzle'] = wine4_rating.sizzle
        initial_data['wine4_sizzle_dnl'] = wine4_rating.sizzle_dnl
      except WineRatingData.DoesNotExist:
        pass

      try:
        wine5_rating = WineRatingData.objects.get(user=taster, wine=wine5)
        initial_data['wine5_overall'] = wine5_rating.overall
        initial_data['wine5_sweet'] = wine5_rating.sweet
        initial_data['wine5_sweet_dnl'] = wine5_rating.sweet_dnl
        initial_data['wine5_weight'] = wine5_rating.weight
        initial_data['wine5_weight_dnl'] = wine5_rating.weight_dnl
        initial_data['wine5_texture'] = wine5_rating.texture
        initial_data['wine5_texture_dnl'] = wine5_rating.texture_dnl
        initial_data['wine5_sizzle'] = wine5_rating.sizzle
        initial_data['wine5_sizzle_dnl'] = wine5_rating.sizzle_dnl
      except WineRatingData.DoesNotExist:
        pass

      try:
        wine6_rating = WineRatingData.objects.get(user=taster, wine=wine6)
        initial_data['wine6_overall'] = wine6_rating.overall
        initial_data['wine6_sweet'] = wine6_rating.sweet
        initial_data['wine6_sweet_dnl'] = wine6_rating.sweet_dnl
        initial_data['wine6_weight'] = wine6_rating.weight
        initial_data['wine6_weight_dnl'] = wine6_rating.weight_dnl
        initial_data['wine6_texture'] = wine6_rating.texture
        initial_data['wine6_texture_dnl'] = wine6_rating.texture_dnl
        initial_data['wine6_sizzle'] = wine6_rating.sizzle
        initial_data['wine6_sizzle_dnl'] = wine6_rating.sizzle_dnl
      except WineRatingData.DoesNotExist:
        pass

    else:
      initial_data['email'] = email

    initial_data['party'] = party

    if request.POST.get('add_taster'):
      taster_form = AddTasterRatingsForm(request.POST)
    else:
      taster_form = AddTasterRatingsForm()
    data['taster_form'] = taster_form

    if taster_form.is_valid():
      try:
        invitee = User.objects.get(email=taster_form.cleaned_data['email'].lower())
      except User.DoesNotExist:
        invitee = taster_form.save()

        # new user was created
        temp_password = User.objects.make_random_password()
        invitee.set_password(temp_password)
        invitee.save()

        verification_code = str(uuid.uuid4())
        vque = VerificationQueue(user=invitee, verification_code=verification_code)
        vque.save()

        # send out verification e-mail, create a verification code
        send_verification_email(request, verification_code, temp_password, invitee.email)

      # link them to party and RSVP
      today = timezone.now()

      invite, created = PartyInvite.objects.get_or_create(party=party, invitee=invitee, invited_by=party.host)
      # only update response times for tasters who had not RSVP'd
      if created:
        invite.response = 3
        invite.response_timestamp = today
        invite.save()

      messages.info(request, "Taster successfully added to this party. Now you can go ahead and add their wine ratings.")
      return HttpResponseRedirect(reverse('record_all_wine_ratings', args=[invitee.email, party.id]))

    if request.POST.get('save_ratings'):
      form = AllWineRatingsForm(request.POST or None, initial=initial_data)
    else:
      form = AllWineRatingsForm(initial=initial_data)

    if form.is_valid():
      results = form.save()

      if np.sum(np.array([results[1].overall, results[2].overall,
                          results[3].overall, results[4].overall,
                          results[5].overall, results[6].overall]) > 0) == 6:
        # only save personality if all 6 wine fields have been filled out
        personality = calculate_wine_personality(*results)
        data["personality"] = personality
        data['can_order_for_taster'] = True

        if pro_group in u.groups.all():
          # ask if you want to fill out next customer's ratings or order wine
          data["role"] = "pro"
          # log the time and the party that the persona was found
          if party:
            persona_log, created = PersonaLog.objects.get_or_create(user=taster)
            persona_log.pro = u
            if created or persona_log.party is None:
              # record first party
              persona_log.party = party
            persona_log.save()

        elif tas_group in u.groups.all():
          # saving your own data
          data["role"] = "taster"
          if party:
            persona_log, created = PersonaLog.objects.get_or_create(user=taster)
            if persona_log.party is None:
              # if no previous log has been created, since we only track the first party
              persona_log.party = party
              persona_log.save()
          else:
            # saved before or without the party
            PersonaLog.objects.get_or_create(user=taster)
        elif hos_group in u.groups.all():
          # personality was created by an host herself
          # ask if you want order wine
          data["role"] = "host"
          PersonaLog.objects.get_or_create(user=taster)
          today = timezone.now()

          data['can_order_for_taster'] = (today - party.event_date <= timedelta(hours=24))

        return render_to_response("personality/ratings_saved.html", data, context_instance=RequestContext(request))
      else:
        msg = "Partial ratings have been saved for %s. <a href='%s'>Enter ratings for next taster.</a>" % (taster.email, reverse('party_details', args=[party.id]))
        messages.success(request, msg)

    data["rate_wines_menu"] = True
    data["form"] = form

    if not rate and taster.get_profile().has_personality():
      data['personality'] = taster.get_profile().wine_personality
      data["invitee"] = taster
      data['role'] = u.get_profile().role()
      today = timezone.now()
      data['can_order_for_taster'] = (today - party.event_date <= timedelta(hours=24))

      return render_to_response("personality/ratings_saved.html", data, context_instance=RequestContext(request))
    else:
      return render_to_response("personality/record_all_wine_ratings.html", data, context_instance=RequestContext(request))

  else:
    #else of - if (pro_group in u.groups.all()) or (tas_group in u.groups.all()) or (hos_group in u.groups.all()):

    # user needs to be a Vinely Pro or Vinely Taster to fill this out
    # Vinely Taster is filling out their own data
    raise PermissionDenied


@login_required
def taster_list(request, taster, party_id):
  pro = request.user
  taster = taster.strip()
  
  # only get tasters linked to this pro
  att_group = Group.objects.get(name="Vinely Taster")

  # show people who RSVP'ed to the party
  my_guests = PartyInvite.objects.filter(party__organizedparty__pro=pro, party__id=party_id)
  users = User.objects.filter(id__in = [x.invitee.id for x in my_guests]) # , groups__in=[att_group])
  users = users.filter(Q(first_name__icontains=taster) | Q(last_name__icontains=taster) | Q(email__icontains=taster)).order_by('first_name')
  data = ['%s %s, %s' % (x.first_name, x.last_name, x.email) for x in users]

  return HttpResponse(json.dumps(data), mimetype="application/json")

