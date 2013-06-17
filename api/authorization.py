from tastypie.exceptions import Unauthorized
from tastypie.authorization import Authorization


# Ref: https://django-tastypie.readthedocs.org/en/latest/authorization.html#implementing-your-own-authorization
class UserObjectsOnlyAuthorization(Authorization):
  """
  Allow users to only modify their own objects
  """
  def read_list(self, object_list, bundle):
    # This assumes a ``QuerySet`` from ``ModelResource``.
    model_name = object_list.model.__name__
    if model_name == 'User':
      return object_list.filter(id=bundle.request.user.id)
    elif model_name == 'Party':
      return object_list.filter(party_invite__invitee=bundle.request.user)
    elif model_name == 'PartyInvite':
      return object_list.filter(invitee=bundle.request.user)
    else:
      return object_list.filter(user=bundle.request.user)

  def read_detail(self, object_list, bundle):
    # Is the requested object owned by the user?
    model_name = object_list.model.__name__
    if model_name == 'User':
      return bundle.obj.id == bundle.request.user.id
    elif model_name == 'Party':
      return bundle.obj.partyinvite.invitee == bundle.request.user
    elif model_name == 'PartyInvite':
      return bundle.obj.invitee == bundle.request.user
    else:
      return bundle.obj.user == bundle.request.user

  def create_list(self, object_list, bundle):
    # Assuming their auto-assigned to ``user``.
    return object_list

  def create_detail(self, object_list, bundle):
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
