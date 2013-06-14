
from personality.models import WinePersonality, WineRatingData
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication, BasicAuthentication, MultiAuthentication
from tastypie.authorization import Authorization  # , DjangoAuthorization
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.exceptions import Unauthorized
from tastypie.utils import trailing_slash
from tastypie import fields
from tastypie.validation import FormValidation

from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url
from django.contrib.sessions.models import Session

from accounts.models import User, UserProfile
from main.models import Party, PartyInvite, Address

from personality.forms import WineRatingForm
from accounts.forms import MakeTasterForm

import base64


class DjangoCookieEmailAuthentication(BasicAuthentication):
  '''
   If the user is already authenticated by a django session it will
   allow the request (useful for ajax calls) . If it is not, defaults
   to basic authentication, which other clients could use.
  '''
  def is_authenticated(self, request, **kwargs):
    if 'sessionid' in request.COOKIES:
      try:
        s = Session.objects.get(pk=request.COOKIES['sessionid'])
        if '_auth_user_id' in s.get_decoded():
          u = User.objects.get(id=s.get_decoded()['_auth_user_id'])
          request.user = u
          return True
      except Session.DoesNotExist:
        pass

    if not request.META.get('HTTP_AUTHORIZATION'):
      return self._unauthorized()

    try:
      (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()
      if auth_type.lower() != 'basic':
        return self._unauthorized()
      user_pass = base64.b64decode(data)
    except:
      return self._unauthorized()

    bits = user_pass.split(':', 1)

    if len(bits) != 2:
      return self._unauthorized()

    if self.backend:
      user = self.backend.authenticate(email=bits[0], password=bits[1])
    else:
      user = authenticate(email=bits[0], password=bits[1])

    if user is None:
      return self._unauthorized()

    if not self.check_active(user):
      return False

    request.user = user
    return True


class SignupResource(ModelResource):
  phone = fields.CharField()
  zipcode = fields.CharField()

  class Meta:
    allowed_methods = ['post']
    queryset = User.objects.all()
    include_resource_uri = False
    fields = ['email', 'first_name', 'last_name', 'password', 'zipcode', 'phone']
    resource_name = 'auth/signup'
    validation = FormValidation(form_class=MakeTasterForm)
    authorization = Authorization()

  # def prepend_urls(self):
  #   # request.META.get('HTTP_AUTHORIZATION')
  #   return [
  #       url(r"^(?P<resource_name>%s)%s$" %
  #           (self._meta.resource_name, trailing_slash()),
  #           self.wrap_view('signup'), name="api_signup"),
  #   ]


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
        return self.create_response(request, {
            'success': True
        })
      else:
        return self.create_response(request, {
            'success': False,
            'reason': 'disabled',
        }, HttpForbidden)
    else:
      return self.create_response(request, {
          'success': False,
          'reason': 'incorrect username or password',
      }, HttpUnauthorized)


class LogoutResource(ModelResource):
  class Meta:
    queryset = User.objects.all()
    fields = ['']
    resource_name = 'auth/logout'
    allowed_methods = ['get']
    detail_allowed_methods = []
    limit = 0
    include_resource_uri = False

  def prepend_urls(self):
    return [
        url(r'^(?P<resource_name>%s)%s$' %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('logout'), name='api_logout'),
    ]

  def logout(self, request, **kwargs):
    self.method_check(request, allowed=['get'])
    if request.user and request.user.is_authenticated():
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
    # authorization = Authorization()
    authentication = SessionAuthentication()

  def obj_get_list(self, bundle, **kwargs):
    # only return parties for logged in user
    user = bundle.request.user
    today = timezone.now()
    objects = super(PartyResource, self).obj_get_list(bundle, **kwargs)
    filtered_objects = objects.filter(partyinvite__invitee__id=user.id, event_date__gt=today).order_by('event_date')
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
    filtered_objects = objects.filter(event_date__gt=today)
    return filtered_objects


class PartyInviteResource(ModelResource):
  party = fields.ToOneField(PartyResource, 'party')

  class Meta:
    queryset = PartyInvite.objects.all()
    allowed_methods = ['get', 'put', 'post']
    # authorization = Authorization()
    authentication = SessionAuthentication()

  def obj_get_list(self, bundle, **kwargs):
    # only return invitations for logged in user
    user = bundle.request.user
    today = timezone.now()
    objects = super(PartyInviteResource, self).obj_get_list(bundle, **kwargs)
    filtered_objects = objects.filter(invitee__id=user.id, party__event_date__gt=today)
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
    authorization = Authorization()
    authentication = SessionAuthentication()
    validation = FormValidation(form_class=WineRatingForm)

  def obj_get(self, bundle, **kwargs):
    # allow user to only see their own rating data
    obj = super(WineRatingDataResource, self).obj_get(bundle, **kwargs)
    user = bundle.request.user

    if WineRatingData.objects.filter(user__id=user.id, id=kwargs.get('pk')).exists():
      return obj
    else:
      return self.unauthorized_result(Unauthorized)

  def obj_get_list(self, bundle, **kwargs):
    # only return winerating data for logged in user
    user = bundle.request.user
    objects = super(WineRatingDataResource, self).obj_get_list(bundle, **kwargs)
    filtered_objects = objects.filter(user__id=user.id)
    return filtered_objects


class ProfileResource(ModelResource):
  personality = fields.ToOneField('api.resources.WinePersonalityResource', 'wine_personality', null=True)

  class Meta:
    queryset = UserProfile.objects.all()
    fields = ['id', 'account_credit', 'club_member', 'dob', 'image', 'phone', 'prequestionnaire', 'role', 'zipcode', 'shipping_address']
    allowed_methods = ['get', 'put']
    # list_allowed_methods = []
    resource_name = 'profile'
    include_resource_uri = True
    # authorization = Authorization()
    authentication = SessionAuthentication()

  def obj_get_list(self, bundle, **kwargs):
    user = bundle.request.user
    objects = super(ProfileResource, self).obj_get_list(bundle, **kwargs)
    filtered_objects = objects.filter(user__id=user.id)
    return filtered_objects


class UserResource(ModelResource):
  profile = fields.ToOneField(ProfileResource, 'userprofile', full=True, null=True)

  class Meta:
    queryset = User.objects.all()
    excludes = ['password', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'username']
    # authorization = Authorization()
    authentication = SessionAuthentication()
    allowed_methods = ['get', 'put']
    # list_allowed_methods = []

  def obj_get_list(self, bundle, **kwargs):
    user = bundle.request.user
    objects = super(UserResource, self).obj_get_list(bundle, **kwargs)
    filtered_objects = objects.filter(id=user.id)
    return filtered_objects
