
from lepl.apps.rfc3696 import Email
from tastypie.resources import ModelResource
from tastypie.authentication import MultiAuthentication
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.utils import trailing_slash
from tastypie import fields
from tastypie.validation import FormValidation
from tastypie.models import ApiKey
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url
from django.contrib.sessions.models import Session
from django.conf import settings

from api.auth import UserObjectsOnlyAuthorization, EmailApiKeyAuthentication, TestSessionAuthentication

from accounts.models import User, UserProfile
from accounts.forms import NameEmailUserMentorCreationForm

from main.forms import PartyInviteTasterForm
from main.models import Party, PartyInvite, Address

from personality.models import WinePersonality, WineRatingData, Wine
from personality.forms import WineRatingForm

from api.fields import Base64FileField

import uuid

email_validator = Email()


if settings.DEPLOY:
  authentication_backends = [EmailApiKeyAuthentication()]
else:
  authentication_backends = [TestSessionAuthentication(), EmailApiKeyAuthentication()]


class SignupResource(ModelResource):
  phone_number = fields.CharField()
  zipcode = fields.CharField()

  class Meta:
    allowed_methods = ['post']
    queryset = User.objects.all()
    include_resource_uri = False
    fields = ['email', 'first_name', 'last_name', 'password', 'zipcode', 'phone']
    resource_name = 'auth/signup'
    validation = FormValidation(form_class=NameEmailUserMentorCreationForm)
    authorization = Authorization()
    always_return_data = True

  def full_hydrate(self, bundle):
    # form validation expects fields password1 and password2
    bundle.data['password1'] = bundle.data.get('password')
    bundle.data['password2'] = bundle.data.get('password')
    return super(SignupResource, self).full_hydrate(bundle)

  def full_dehydrate(self, bundle):
    bundle = super(SignupResource, self).full_dehydrate(bundle)
    # don't show password in data presented to user
    del bundle.data['password1']
    del bundle.data['password2']
    del bundle.data['password']

    profile = bundle.obj.get_profile()
    bundle.data['phone_number'] = profile.phone
    bundle.data['zipcode'] = profile.zipcode
    return bundle

  def obj_create(self, bundle, **kwargs):
    for key, value in kwargs.items():
      setattr(bundle.obj, key, value)

    bundle = self.full_hydrate(bundle)
    bundle.obj.set_password(bundle.data.get('password'))
    bundle.obj.is_active = True
    bundle = self.save(bundle)

    profile = bundle.obj.get_profile()
    profile.phone = bundle.data.get('phone_number')
    profile.zipcode = bundle.data.get('zipcode')
    profile.save()
    return bundle


class LoginResource(ModelResource):
  class Meta:
    queryset = User.objects.all()
    fields = ['email', 'password']
    resource_name = 'auth/login'
    allowed_methods = ['post']
    detail_allowed_methods = []
    limit = 0
    include_resource_uri = False

  def prepend_urls(self):
    return [
        url(r"^(?P<resource_name>%s)%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('login'), name="api_login"),
    ]

  def login(self, request, **kwargs):
    self.method_check(request, allowed=['post'])

    data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

    email = data.get('email', '')
    password = data.get('password', '')

    user = authenticate(email=email, password=password)
    if user:
      if user.is_active:
        login(request, user)
        api_key, created = ApiKey.objects.get_or_create(user=user)
        return self.create_response(request, {
            'api_key': api_key.key,
            'user': user.id
        })
      else:
        return self.create_response(request, {
            'success': False,
            'reason': 'Account disabled',
        }, HttpForbidden)
    else:
      return self.create_response(request, {
          'success': False,
          'reason': 'Incorrect username or password',
      }, HttpUnauthorized)


class LogoutResource(ModelResource):
  class Meta:
    queryset = User.objects.all()
    fields = ['']
    resource_name = 'auth/logout'
    allowed_methods = ['get']
    detail_allowed_methods = []
    authentication = MultiAuthentication(*authentication_backends)
    authorization = UserObjectsOnlyAuthorization()
    limit = 0
    include_resource_uri = False

  def get_list(self, request, **kwargs):
    if request.user and request.user.is_authenticated() or self.is_authenticated(request):
      ApiKey.objects.filter(user=request.user).delete()
      logout(request)
      Session.objects.filter(pk=request.COOKIES.get('sessionid')).delete()
      return self.create_response(request, {'success': True})
    else:
      return self.create_response(request, {'success': False}, HttpUnauthorized)


class AddressResource(ModelResource):
  class Meta:
    queryset = Address.objects.all()
    excludes = ['id', 'nick_name', 'resource_uri']
    include_resource_uri = False


class PartyResource(ModelResource):
  address = fields.ToOneField(AddressResource, 'address', full=True)
  host = fields.ToOneField('api.resources.UserResource', 'host', null=True)
  is_event = fields.BooleanField()

  class Meta:
    queryset = Party.objects.all()  # exclude(host__email='events@vinely.com')
    allowed_methods = ['get']
    fields = ['title', 'description', 'id', 'fee', 'event_date', 'phone', 'is_event']
    # authorization = UserObjectsOnlyAuthorization()
    authorization = Authorization()
    authentication = MultiAuthentication(*authentication_backends)
    filtering = {
        "host": ALL_WITH_RELATIONS,
        'host__email': ['iexact']
    }

  def dehydrate_is_event(self, bundle):
    return bundle.obj.is_events_party

  def obj_get_list(self, bundle, **kwargs):
    # only return future parties
    today = timezone.now()
    objects = super(PartyResource, self).obj_get_list(bundle, **kwargs)
    # filtered_objects = objects.filter(event_date__gt=today, confirmed=True).order_by('event_date')
    filtered_objects = objects.filter(event_date__gt=today).order_by('event_date')
    invitee_filter = bundle.request.GET.get('me', None)
    if invitee_filter:
      return filtered_objects.filter(partyinvite__invitee__id=bundle.request.user.id)
    # if invitee_filter:
    #   filtered_objects = filtered_objects.filter(partyinvite__invitee__id=invitee_filter, partyinvite__invitee__id=bundle.obj.id)
    return filtered_objects


class EventResource(ModelResource):
  class Meta:
    queryset = Party.objects.filter(host__email='events@vinely.com')
    fields = ['title', 'description', 'id', 'fee', 'event_date', 'phone']
    resource_name = 'event'
    allowed_methods = ['get']

  def obj_get_list(self, bundle, **kwargs):
    today = timezone.now()
    objects = super(EventResource, self).obj_get_list(bundle, **kwargs)
    filtered_objects = objects.filter(event_date__gt=today).order_by('event_date')
    return filtered_objects


#TODO: only allow updating the response field
class PartyInviteResource(ModelResource):
  party = fields.ToOneField(PartyResource, 'party')
  invitee = fields.ToOneField('api.resources.UserResource', 'invitee')

  class Meta:
    queryset = PartyInvite.objects.all()
    excludes = ['response_timestamp', 'attended', 'invited_timestamp']
    allowed_methods = ['get', 'put', 'post']
    authorization = UserObjectsOnlyAuthorization()
    authentication = MultiAuthentication(*authentication_backends)
    validation = FormValidation(form_class=PartyInviteTasterForm)
    # always_return_data = True

  def obj_get_list(self, bundle, **kwargs):
    # only return future invitations
    today = timezone.now()
    objects = super(PartyInviteResource, self).obj_get_list(bundle, **kwargs)
    filtered_objects = objects.filter(party__event_date__gt=today).order_by('party__event_date')
    return filtered_objects

  def obj_create(self, bundle, **kwargs):
    # TODO: Allow passing invitee as uri instead of dict only
    for key, value in kwargs.items():
      setattr(bundle.obj, key, value)

    # if new invitee was sent as dict creation will be done during form validation
    invitee_data = bundle.data.get('invitee', {})
    if invitee_data and isinstance(invitee_data, dict):
      invitee_data = bundle.data.pop('invitee', {})
      bundle.data['invitee'] = None
    bundle = self.full_hydrate(bundle)

    for key, value in invitee_data.items():
      bundle.data[key] = value

    bundle.data['party'] = bundle.obj.party_id
    bundle.obj.rsvp_code = str(uuid.uuid4())
    bundle.obj.invited_by = bundle.request.user
    bundle.obj.response = 0
    bundle = self.save(bundle)
    return bundle

  def obj_update(self, bundle, skip_errors=False, **kwargs):
    # this is set so that form validation does not freak out invited error
    bundle.data['change_rsvp'] = 't'
    return super(PartyInviteResource, self).obj_update(bundle, skip_errors, **kwargs)


class WinePersonalityResource(ModelResource):
  class Meta:
    queryset = WinePersonality.objects.all()
    allowed_methods = ['get']
    resource_name = 'personality'
    # authorization = Authorization()
    # authentication = SessionAuthentication()


class WineResource(ModelResource):
  class Meta:
    queryset = Wine.objects.filter(active=True)
    allowed_methods = ['get']
    list_allowed_methods = []
    fields = ['name']


class WineRatingDataResource(ModelResource):
  wine = fields.ToOneField(WineResource, 'wine')
  user = fields.ToOneField('api.resources.UserResource', 'user')

  class Meta:
    queryset = WineRatingData.objects.all()
    excludes = ['timestamp']
    allowed_methods = ['get', 'put', 'post']
    resource_name = 'rating'
    authorization = UserObjectsOnlyAuthorization()
    authentication = MultiAuthentication(*authentication_backends)
    validation = FormValidation(form_class=WineRatingForm)

  def obj_create(self, bundle, **kwargs):
    for key, value in kwargs.items():
      setattr(bundle.obj, key, value)

    bundle = self.full_hydrate(bundle)
    # form validation is failing with uri data
    bundle.data['user'] = bundle.obj.user_id
    bundle.data['wine'] = bundle.obj.wine_id
    bundle = self.save(bundle)
    return bundle


class ProfileResource(ModelResource):
  image = Base64FileField('image')
  personality = fields.ToOneField('api.resources.WinePersonalityResource', 'wine_personality', null=True)

  class Meta:
    queryset = UserProfile.objects.all()
    fields = ['id', 'account_credit', 'club_member', 'dob', 'image', 'phone', 'prequestionnaire', 'role', 'zipcode', 'shipping_address']
    allowed_methods = ['get', 'put']
    # list_allowed_methods = []
    resource_name = 'profile'
    include_resource_uri = True
    authorization = UserObjectsOnlyAuthorization()
    authentication = MultiAuthentication(*authentication_backends)
    always_return_data = True


class UserResource(ModelResource):
  profile = fields.ToOneField(ProfileResource, 'userprofile', full=True, null=True)

  class Meta:
    queryset = User.objects.all()
    excludes = ['password', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'username']
    authorization = UserObjectsOnlyAuthorization()
    authentication = MultiAuthentication(*authentication_backends)
    allowed_methods = ['get', 'put']
    filtering = {
        'last_name': ['icontains'],
    }
    # list_allowed_methods = []


# TWITTER_SHARE = {
#     'twitter': 'http://twitter.com/intent/tweet?text=Test',
# }

# FB_SHARE = {
#     'facebook': 'https://www.facebook.com/sharer/sharer.php?u=vinely.com',
# }

# class ShareResource(ModelResource):
#   link = fields.CharField()
#   text = fields.CharField()

#   class Meta:
#     # object_class = Document
#     queryset = User.objects.all()
#     # fields = ['link', 'text']
#     allowed_methods = ['get']
#     detail_allowed_methods = []
#     include_resource_uri = False
#     # authorization = UserObjectsOnlyAuthorization()
#     # authentication = MultiAuthentication(*authentication_backends)

#   def get_list(self, request, **kwargs):
#     share_resources = [TWITTER_SHARE, FB_SHARE]
#     return self.create_response(request, share_resources)
