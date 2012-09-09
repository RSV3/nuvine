from django.conf.urls import patterns, include, url

urlpatterns = patterns('support.views',
    url(r'^email/list/$', 'list_emails', name='list_emails'),
    url(r'^email/(?P<email_id>\d+)/$', 'view_email', name='view_email'),
    url(r'^download/users/$', 'download_users', name='download_users'),
    url(r'^download/parties/$', 'download_parties', name='download_parties'),
    url(r'^download/orders/$', 'download_orders', name='download_orders'),
    url(r'^users/$', 'view_users', name='view_users'),
    url(r'^parties/$', 'view_parties', name='view_parties'),
    url(r'^orders/$', 'view_orders', name='view_orders'),
)
