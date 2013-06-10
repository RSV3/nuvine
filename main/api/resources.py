
from personality.models import WinePersonality, WineRatingData
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.utils import trailing_slash

from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url

from accounts.models import User, UserProfile
from main.models import Party, PartyInvite


class PartyResource(ModelResource):
  class Meta:
    queryset = Party.objects.all()


class PartyInviteResource(ModelResource):
  class Meta:
    queryset = PartyInvite.objects.all()


class WinePersonalityResource(ModelResource):
  class Meta:
    queryset = WinePersonality.objects.all()


class WineRatingDataResource(ModelResource):
  class Meta:
    queryset = WineRatingData.objects.all()


class UserResource(ModelResource):
  class Meta:
    queryset = User.objects.all()
    excludes = ['password', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'username']
    authorization = DjangoAuthorization()
    authentication = SessionAuthentication()

  def override_urls(self):
    return [
        url(r"^(?P<resource_name>%s)/login%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('login'), name="api_login"),
        url(r'^(?P<resource_name>%s)/logout%s$' %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('logout'), name='api_logout'),
    ]

  def login(self, request, **kwargs):
    self.method_check(request, allowed=['post'])

    data = self.deserialize(request, request.raw_post_data, format=request.META.get('application/x-www-form-urlencoded'))  # , format=request.META.get('CONTENT_TYPE', 'application/json'))

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

  def logout(self, request, **kwargs):
    self.method_check(request, allowed=['get'])
    if request.user and request.user.is_authenticated():
      logout(request)
      return self.create_response(request, {'success': True})
    else:
      return self.create_response(request, {'success': False}, HttpUnauthorized)


class UserProfileResource(ModelResource):
  class Meta:
    queryset = UserProfile.objects.all()
