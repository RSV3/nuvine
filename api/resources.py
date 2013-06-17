
from personality.models import WinePersonality, WineRatingData
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication, MultiAuthentication, ApiKeyAuthentication  # , BasicAuthentication
from tastypie.authorization import Authorization  # , DjangoAuthorization
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.utils import trailing_slash
from tastypie import fields
from tastypie.validation import FormValidation

# from django.db import models
# from tastypie.models import create_api_key
from tastypie.models import ApiKey
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url
from django.contrib.sessions.models import Session

from accounts.models import User, UserProfile
from main.models import Party, PartyInvite, Address
from api.authorization import UserObjectsOnlyAuthorization
from personality.forms import WineRatingForm
from accounts.forms import NameEmailUserMentorCreationForm

# import base64

# models.signals.post_save.connect(create_api_key, sender=User)


class EmailApiKeyAuthentication(ApiKeyAuthentication):
  def is_authenticated(self, request, **kwargs):
      """
      Finds the user and checks their API key.

      Should return either ``True`` if allowed, ``False`` if not or an
      ``HttpResponse`` if you need something custom.
      """
      from tastypie.compat import User
      try:
          username, api_key = self.extract_credentials(request)
      except ValueError:
          return self._unauthorized()

      if not username or not api_key:
          return self._unauthorized()

      try:
          # use email field instead of username
          lookup_kwargs = {'email': username}
          user = User.objects.get(**lookup_kwargs)
      except (User.DoesNotExist, User.MultipleObjectsReturned):
          return self._unauthorized()

      if not self.check_active(user):
          return False

      key_auth_check = self.get_key(user, api_key)
      if key_auth_check and not isinstance(key_auth_check, HttpUnauthorized):
          request.user = user
      return key_auth_check


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
            'api_key': api_key.key
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
    authentication = MultiAuthentication(SessionAuthentication(), EmailApiKeyAuthentication())
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

  class Meta:
    queryset = Party.objects.exclude(host__email='events@vinely.com')
    allowed_methods = ['get']
    fields = ['title', 'description', 'id', 'fee', 'event_date', 'phone']
    authorization = UserObjectsOnlyAuthorization()
    authentication = MultiAuthentication(SessionAuthentication(), EmailApiKeyAuthentication())

  def obj_get_list(self, bundle, **kwargs):
    # only return future parties
    today = timezone.now()
    objects = super(PartyResource, self).obj_get_list(bundle, **kwargs)
    filtered_objects = objects.filter(event_date__gt=today).order_by('event_date')
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


class PartyInviteResource(ModelResource):
  party = fields.ToOneField(PartyResource, 'party')

  class Meta:
    queryset = PartyInvite.objects.all()
    allowed_methods = ['get', 'put', 'post']
    authorization = UserObjectsOnlyAuthorization()
    authentication = MultiAuthentication(SessionAuthentication(), EmailApiKeyAuthentication())

  def obj_get_list(self, bundle, **kwargs):
    # only return future invitations
    today = timezone.now()
    objects = super(PartyInviteResource, self).obj_get_list(bundle, **kwargs)
    filtered_objects = objects.filter(party__event_date__gt=today).order_by('event_date')
    return filtered_objects


class WinePersonalityResource(ModelResource):
  class Meta:
    queryset = WinePersonality.objects.all()
    allowed_methods = ['get']
    resource_name = 'personality'
    # authorization = Authorization()
    # authentication = SessionAuthentication()


class WineRatingDataResource(ModelResource):
  class Meta:
    queryset = WineRatingData.objects.all()
    excludes = ['timestamp']
    allowed_methods = ['get', 'put', 'post']
    resource_name = 'rating'
    authorization = UserObjectsOnlyAuthorization()
    authentication = MultiAuthentication(SessionAuthentication(), EmailApiKeyAuthentication())
    validation = FormValidation(form_class=WineRatingForm)


class ProfileResource(ModelResource):
  personality = fields.ToOneField('api.resources.WinePersonalityResource', 'wine_personality', null=True)

  class Meta:
    queryset = UserProfile.objects.all()
    fields = ['id', 'account_credit', 'club_member', 'dob', 'image', 'phone', 'prequestionnaire', 'role', 'zipcode', 'shipping_address']
    allowed_methods = ['get', 'put']
    # list_allowed_methods = []
    resource_name = 'profile'
    include_resource_uri = True
    authorization = UserObjectsOnlyAuthorization()
    authentication = MultiAuthentication(SessionAuthentication(), EmailApiKeyAuthentication())


class UserResource(ModelResource):
  profile = fields.ToOneField(ProfileResource, 'userprofile', full=True, null=True)

  class Meta:
    queryset = User.objects.all()
    excludes = ['password', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'username']
    authorization = UserObjectsOnlyAuthorization()
    authentication = MultiAuthentication(SessionAuthentication(), EmailApiKeyAuthentication())
    allowed_methods = ['get', 'put']
    # list_allowed_methods = []
