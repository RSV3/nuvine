
from personality.models import WinePersonality, WineRatingData
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.utils import trailing_slash
from tastypie import fields

from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url

from accounts.models import User, UserProfile
from main.models import Party, PartyInvite


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
      return self.create_response(request, {'success': True})
    else:
      return self.create_response(request, {'success': False}, HttpUnauthorized)


class PartyResource(ModelResource):
  class Meta:
    queryset = Party.objects.all()
    resource_name = 'parties'
    allowed_methods = ['get', 'put', 'post']
    authorization = DjangoAuthorization()
    authentication = SessionAuthentication()


class PartyInviteResource(ModelResource):
  party = fields.ForeignKey(PartyResource, 'party')

  class Meta:
    queryset = PartyInvite.objects.all()
    allowed_methods = ['get', 'put', 'post']
    authorization = DjangoAuthorization()
    authentication = SessionAuthentication()


class WinePersonalityResource(ModelResource):
  class Meta:
    queryset = WinePersonality.objects.all()
    allowed_methods = ['get']
    authorization = DjangoAuthorization()
    authentication = SessionAuthentication()


class WineRatingDataResource(ModelResource):
  class Meta:
    queryset = WineRatingData.objects.all()
    allowed_methods = ['get', 'put', 'post']
    authorization = DjangoAuthorization()
    authentication = SessionAuthentication()


class ProfileResource(ModelResource):
  user = fields.ToOneField('UserResource', 'profile')

  class Meta:
    queryset = UserProfile.objects.all()
    allowed_methods = ['get', 'put', 'post']
    authorization = DjangoAuthorization()
    authentication = SessionAuthentication()


class UserResource(ModelResource):
  profile = fields.ToOneField(ProfileResource, 'profile')

  class Meta:
    queryset = User.objects.all()
    excludes = ['password', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'username']
    authorization = DjangoAuthorization()
    authentication = SessionAuthentication()
    allowed_methods = ['get', 'put', 'post']


class CreateUserResource(ModelResource):
  class Meta:
    allowed_methods = ['post']
    object_class = User
    include_resource_uri = False
    fields = ['username']

  def obj_create(self, bundle, request=None, **kwargs):
    try:
      bundle = super(CreateUserResource, self).obj_create(bundle, request, **kwargs)
    except:
      raise Exception('That username already exists')
    return bundle
