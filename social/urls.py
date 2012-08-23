from django.conf.urls import patterns, include, url

urlpatterns = patterns('social.views',
    url(r'^xoauth/$', 'get_xoauth_gmail', name='get_xoauth_gmail'),
)
