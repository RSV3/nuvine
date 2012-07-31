from django.conf.urls import patterns, include, url

urlpatterns = patterns('main.views',
    url(r'^home/$', 'home', name='home_page'),
    url(r'^about/$', 'about', name='about'),
    url(r'^contact/$', 'contact_us', name='contact_us'),
    url(r'^howto/$', 'how_it_works', name='how_it_works'),

    url(r'^host/party/$', 'host_vinely_party', name='host_vinely_party'),

    url(r'^party/list/$', 'party_list', name='party_list'),
    url(r'^party/add/$', 'party_add', name='party_add'),
    url(r'^party/attendee/list/(?P<party_id>\d+)/$', 'party_attendee_list', name='party_attendee_list'),
    url(r'^party/attendee/invite/(?P<party_id>\d+)/$', 'party_attendee_invite', name='party_attendee_invite'),
    url(r'^party/attendee/invite/$', 'party_attendee_invite', name='party_attendee_invite'),
    url(r'^party/order/list/(?P<party_id>\d+)/$', 'party_order_list', name='party_order_list'),

    url(r'^ratings/record/$', 'record_wine_ratings', name='record_wine_ratings'),
    url(r'^ratings/record/all/$', 'record_all_wine_ratings', name='record_all_wine_ratings'),
    url(r'^ratings/record/all/(?P<email>[@\w\+\-\.]+)/$', 'record_all_wine_ratings', name='record_all_wine_ratings'),
    url(r'^order/start/$', 'start_order', name='start_order'),
    url(r'^cart/add/wine/(?P<level>\w+)/$', 'cart_add_wine', name='cart_add_wine'),
    url(r'^cart/add/tasting/kit/$', 'cart_add_tasting_kit', name='cart_add_tasting_kit'),
    url(r'^cart/remove/(?P<cart_id>\d+)/(?P<item_id>\d+)/$', 'cart_remove_item', name='cart_remove_item'),
    url(r'^cart/$', 'cart', name='cart'),
    url(r'^cart/customize/$', 'customize_checkout', name='customize_checkout'),
    url(r'^order/place/$', 'place_order', name='place_order'),
    url(r'^order/complete/(?P<order_id>[\-\w]+)/$', 'order_complete', name='order_complete'),
    url(r'^order/history/$', 'order_history', name='order_history'),

    url(r'^supplier/party/list/$', 'supplier_party_list', name='supplier_party_list'),
    url(r'^orders/pending/$', 'pending_orders', name='pending_orders'),
    url(r'^orders/fulfilled/$', 'fulfilled_orders', name='fulfilled_orders'),
    url(r'^orders/all/$', 'all_orders', name='all_orders'),
    url(r'^edit/subscription/$', 'edit_subscription', name='edit_subscription'),
    url(r'^edit/credit/$', 'edit_credit_card', name='edit_credit_card'),
    url(r'^edit/shipping/$', 'edit_shipping_address', name='edit_shipping_address'),
)
