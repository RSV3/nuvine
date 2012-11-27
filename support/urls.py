from django.conf.urls import patterns, include, url

urlpatterns = patterns('support.views',
    url(r'^$', 'admin_index', name='admin_index'),
    url(r'^subscriptions/manage/$', 'manage_subscriptions', name='manage_subscriptions'),
    url(r'^email/list/$', 'list_emails', name='list_emails'),
    url(r'^email/(?P<email_id>\d+)/$', 'view_email', name='view_email'),
    url(r'^download/users/$', 'download_users', name='download_users'),
    url(r'^download/users/party/(?P<party_id>\d+)/$', 'download_users_from_party', name="download_users_from_party"),
    url(r'^download/parties/$', 'download_parties', name='download_parties'),
    url(r'^download/orders/$', 'download_orders', name='download_orders'),
    url(r'^users/$', 'view_users', name='view_users'),
    url(r'^parties/$', 'view_parties', name='view_parties'),
    url(r'^orders/$', 'view_orders', name='view_orders'),
)
