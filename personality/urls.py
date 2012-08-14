from django.conf.urls import patterns, include, url

urlpatterns = patterns('personality.views',
    url(r'^me/$', 'my_wine_personality', name='my_wine_personality'),
    url(r'^details/(?P<user_id>\d+)/(?P<order_id>[\-\w]+)/$', 'personality_details', name="personality_details"),
    url(r'^pre/questionnaire/general/$', 'pre_questionnaire_general', name='pre_questionnaire_general'),
    url(r'^pre/questionnaire/wine/$', 'pre_questionnaire_wine', name='pre_questionnaire_wine'),
)
