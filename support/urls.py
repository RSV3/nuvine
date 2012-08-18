from django.conf.urls import patterns, include, url

urlpatterns = patterns('support.views',
    url(r'^email/list/$', 'list_emails', name='list_emails'),
    url(r'^email/(?P<email_id>\d+)/$', 'view_email', name='view_email'),
)
