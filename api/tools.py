from tastypie.api import Api
from api.resources import UserResource, ProfileResource, LoginResource, LogoutResource, SignupResource, \
                                PartyResource, PartyInviteResource, EventResource, \
                                WinePersonalityResource, WineRatingDataResource
# from main.api.resources import AnoterResource, YetAnotherResource

api = Api()

resources = [UserResource, ProfileResource, LoginResource, LogoutResource, SignupResource]
resources += [PartyResource, PartyInviteResource, EventResource]
resources += [WineRatingDataResource, WinePersonalityResource]

for r in resources:
  api.register(r())
