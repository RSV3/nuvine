from tastytools.api import Api
from main.api.resources import UserResource, UserProfileResource, \
                                PartyResource, PartyInviteResource, \
                                WinePersonalityResource, WineRatingDataResource
# from main.api.resources import AnoterResource, YetAnotherResource

api = Api()
api.register(resources=[UserResource, UserProfileResource])
api.register(resources=[PartyResource, PartyInviteResource])
api.register(resources=[WineRatingDataResource, WinePersonalityResource])
