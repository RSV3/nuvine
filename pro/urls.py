from django.conf.urls import patterns, url

urlpatterns = patterns('pro.views',
    url(r'^home/$', 'pro_home', name='pro_home'),
    url(r'^stats/$', 'pro_stats', name='pro_stats'),
)