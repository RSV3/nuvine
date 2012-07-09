from django.conf.urls import patterns, include, url

urlpatterns = patterns('main.views',
    url(r'^home/$', 'home', name='home_page'),
    url(r'^about/$', 'about', name='about'),
    url(r'^contact/$', 'contact_us', name='contact_us'),

    url(r'^ratings/record/$', 'record_wine_ratings', name='record_wine_ratings'),
    url(r'^ratings/record/all/$', 'record_all_wine_ratings', name='record_all_wine_ratings'),
    url(r'^order/start/$', 'start_order', name='start_order'),

    url(r'^signup/party_specialist/$', 'signup_party_specialist', name='signup_party_specialist'),
    url(r'^signup/party_attendee/$', 'signup_party_attendee', name='signup_party_attendee'),
    url(r'^signup/party_host/$', 'signup_party_host', name='signup_party_host'),
)
