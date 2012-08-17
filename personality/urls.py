from django.conf.urls import patterns, include, url

urlpatterns = patterns('personality.views',
    url(r'^me/$', 'my_wine_personality', name='my_wine_personality'),
    url(r'^details/(?P<user_id>\d+)/(?P<order_id>[\-\w]+)/$', 'personality_details', name="personality_details"),
    url(r'^pre/questionnaire/general/$', 'pre_questionnaire_general', name='pre_questionnaire_general'),
    url(r'^pre/questionnaire/wine/$', 'pre_questionnaire_wine', name='pre_questionnaire_wine'),
    url(r'^ratings/record/$', 'record_wine_ratings', name='record_wine_ratings'),
    url(r'^ratings/record/all/$', 'record_all_wine_ratings', name='record_all_wine_ratings'),
    url(r'^ratings/record/all/(?P<email>[@\w\+\-\.]+)/$', 'record_all_wine_ratings', name='record_all_wine_ratings'),
    url(r'^ratings/record/all/(?P<email>[@\w\+\-\.]+)/(?P<party_id>\d+)/$', 'record_all_wine_ratings', name='record_all_wine_ratings'),
)
