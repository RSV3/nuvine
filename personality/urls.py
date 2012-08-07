from django.conf.urls import patterns, include, url

urlpatterns = patterns('personality.views',
    url(r'^me/$', 'my_wine_personality', name='my_wine_personality'),
    url(r'^details/(?P<user_id>\d+)/$', 'personality_details', name="personality_details"),
)
