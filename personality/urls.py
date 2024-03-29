from django.conf.urls import patterns, url

urlpatterns = patterns('personality.views',
    url(r'^me/$', 'my_wine_personality', name='my_wine_personality'),
    url(r'^check/personality/exists/$', 'check_personality_exists', name='check_personality_exists'),
    url(r'^details/(?P<user_id>\d+)/(?P<order_id>[\-\w]+)/$', 'personality_details', name="personality_details"),
    url(r'^pre/questionnaire/general/$', 'pre_questionnaire_general', name='pre_questionnaire_general'),
    url(r'^pre/questionnaire/general/(?P<rsvp_code>[\-\w]{36})/$', 'pre_questionnaire_general', name='pre_questionnaire_general'),
    url(r'^pre/questionnaire/wine/$', 'pre_questionnaire_wine', name='pre_questionnaire_wine'),
    url(r'^pre/questionnaire/wine/(?P<rsvp_code>[\-\w]{36})/$', 'pre_questionnaire_wine', name='pre_questionnaire_wine'),
    url(r'^ratings/record/$', 'record_wine_ratings', name='record_wine_ratings'),
    # url(r'^ratings/record/all/$', 'record_all_wine_ratings', name='record_all_wine_ratings'),
    # url(r'^ratings/record/all/(?P<email>[@\w\+\-\.]+)/$', 'record_all_wine_ratings', name='record_all_wine_ratings'),
    url(r'^ratings/record/all/(?P<email>.+)/(?P<party_id>\d+)/$', 'record_all_wine_ratings', name='record_all_wine_ratings'),
    url(r'^ratings/info/(?P<email>.+)/(?P<party_id>\d+)/$', 'personality_rating_info', name='personality_rating_info'),
    url(r'^taster/list/(?P<taster>.+)/(?P<party_id>\d+)/$', 'taster_list', name='taster_list'),
    url(r'^member/ratings/(?P<wine_id>\d+)/$', 'member_rate_wines', name='member_rate_wines'),
    url(r'^member/ratings/overview/$', 'member_ratings_overview', name='member_ratings_overview'),
    url(r'^member/reveal/personality/$', 'member_reveal_personality', name='member_reveal_personality'),

)
