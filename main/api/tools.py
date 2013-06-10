from tastypie.api import Api
from main.api.resources import UserResource, UserProfileResource, \
                                PartyResource, PartyInviteResource, \
                                WinePersonalityResource, WineRatingDataResource
# from main.api.resources import AnoterResource, YetAnotherResource

api = Api()

resources = [UserResource, UserProfileResource]
resources += [PartyResource, PartyInviteResource]
resources += [WineRatingDataResource, WinePersonalityResource]

for r in resources:
  api.register(r())
