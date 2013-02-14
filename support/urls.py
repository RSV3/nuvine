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
    url(r'^orders/(?P<order_id>\d+)/$', 'view_orders', name='view_orders'),
    url(r'^order/edit/$', 'edit_order', name='edit_order'),
    url(r'^order/edit/(?P<order_id>\d+)/$', 'edit_order', name='edit_order'),
    url(r'^order/rate/(?P<order_id>\d+)/$', 'rate_order', name='rate_order'),
    url(r'^orders/past/$', 'view_past_orders', name='view_past_orders'),
    url(r'^orders/past/(?P<order_id>\d+)/$', 'view_past_orders', name='view_past_orders'),
    url(r'^wine/inventory/$', 'wine_inventory', name='wine_inventory'),
    url(r'^download/ready/orders/$', 'download_ready_orders', name='download_ready_orders'),
)
