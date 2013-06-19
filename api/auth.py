from tastypie.exceptions import Unauthorized
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication, ApiKeyAuthentication
from tastypie.http import HttpUnauthorized

from django.utils.http import same_origin
from django.middleware.csrf import _sanitize_token, constant_time_compare
from tastypie.compat import User, username_field
from django.conf import settings


class EmailApiKeyAuthentication(ApiKeyAuthentication):
  def is_authenticated(self, request, **kwargs):
      """
      Finds the user and checks their API key.

      Should return either ``True`` if allowed, ``False`` if not or an
      ``HttpResponse`` if you need something custom.
      """
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


class TestSessionAuthentication(Authentication):
  def is_authenticated(self, request, **kwargs):
    """
    Checks to make sure the user is logged in & has a Django session.

    Similar to SessionAuthentication but checks CSRF_COOKIE instead of HTTP_X_CSRFTOKEN
    """
    if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
      return request.user.is_authenticated()

    if getattr(request, '_dont_enforce_csrf_checks', False):
      return request.user.is_authenticated()

    csrf_token = _sanitize_token(request.COOKIES.get(settings.CSRF_COOKIE_NAME, ''))

    if request.is_secure():
      referer = request.META.get('HTTP_REFERER')

      if referer is None:
        return False

      good_referer = 'https://%s/' % request.get_host()

      if not same_origin(referer, good_referer):
        return False

    request_csrf_token = request.META.get('CSRF_COOKIE', '')

    if not constant_time_compare(request_csrf_token, csrf_token):
      return False

    return request.user.is_authenticated()

  def get_identifier(self, request):
    """
    Provides a unique string identifier for the requestor.

    This implementation returns the user's username.
    """
    return getattr(request.user, username_field)


# Ref: https://django-tastypie.readthedocs.org/en/latest/authorization.html#implementing-your-own-authorization
class UserObjectsOnlyAuthorization(Authorization):
  """
  Allow users to only modify their own objects
  """
  def read_list(self, object_list, bundle):
    print 'read_list'
    # This assumes a ``QuerySet`` from ``ModelResource``.
    model_name = object_list.model.__name__
    if model_name == 'User':
      return object_list.filter(id=bundle.request.user.id)
    elif model_name == 'Party':
      return object_list.filter(partyinvite__invitee=bundle.request.user)
    elif model_name == 'PartyInvite':
      return object_list.filter(invitee=bundle.request.user)
    else:
      return object_list.filter(user=bundle.request.user)

  def read_detail(self, object_list, bundle):
    print 'read_detail', bundle.obj.id
    # Is the requested object owned by the user?
    model_name = object_list
    if model_name == 'User':
      return bundle.obj.id == bundle.request.user.id
    elif model_name == 'Party':
      return bundle.obj.partyinvite_set.filter(invitee=bundle.request.user).exists()
    elif model_name == 'PartyInvite':
      return bundle.obj.invitee == bundle.request.user
    else:
      return bundle.obj.user == bundle.request.user

  def create_list(self, object_list, bundle):
    print 'create_list'
    # Assuming their auto-assigned to ``user``.
    return object_list

  def create_detail(self, object_list, bundle):
    print 'create_detail'
    return self.read_detail(object_list, bundle)

  def update_list(self, object_list, bundle):
    # allowed = []

    # # Since they may not all be saved, iterate over them.
    # for obj in object_list:
    #     if obj.user == bundle.request.user:
    #         allowed.append(obj)

    # return allowed

    # for now dont allow update_list
    return []

  def update_detail(self, object_list, bundle):
    return self.read_detail(object_list, bundle)

  def delete_list(self, object_list, bundle):
    # Sorry user, no deletes for you!
    raise Unauthorized("Sorry, no deletes.")

  def delete_detail(self, object_list, bundle):
    raise Unauthorized("Sorry, no deletes.")
