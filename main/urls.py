from django.conf.urls import patterns, include, url

urlpatterns = patterns('main.views',
    url(r'^home/$', 'home', name='home_page'),
    url(r'^our/story/$', 'our_story', name='our_story'),
    url(r'^get/started/$', 'get_started', name='get_started'),
    url(r'^contact/$', 'contact_us', name='contact_us'),
    url(r'^howto/$', 'how_it_works', name='how_it_works'),
    url(r'^become/vip/$', 'become_vip', name='become_vip'),
    url(r'^dashboard/$', 'dashboard', name='dashboard'),
    url(r'^rate/wines/$', 'rate_wines', name='rate_wines'),

    url(r'^host/party/$', 'host_vinely_party', name='host_vinely_party'),

    url(r'^party/list/$', 'party_list', name='party_list'),
    url(r'^party/add/$', 'party_add', name='party_add'),
    url(r'^party/details/(?P<party_id>\d+)/$', 'party_details', name='party_details'),
    url(r'^party/rsvp/(?P<party_id>\d+)/$', 'party_rsvp', name='party_rsvp'),
    url(r'^party/rsvp/(?P<party_id>\d+)/(?P<response>\d+)/$', 'party_rsvp', name='party_rsvp'),
    url(r'^party/customize/invite/$', 'party_customize_invite', name='party_customize_invite'),
    url(r'^party/send/invites/$', 'party_send_invites', name='party_send_invites'),
    url(r'^party/taster/list/(?P<party_id>\d+)/$', 'party_taster_list', name='party_taster_list'),
    url(r'^party/taster/invite/(?P<party_id>\d+)/$', 'party_taster_invite', name='party_taster_invite'),
    url(r'^party/taster/invite/$', 'party_taster_invite', name='party_taster_invite'),


    url(r'^order/start/$', 'start_order', name='start_order'),
    url(r'^order/start/(?P<receiver_id>\d+)/$', 'start_order', name='start_order'),
    url(r'^order/start/(?P<receiver_id>\d+)/(?P<party_id>\d+)/$', 'start_order', name='start_order'),
    url(r'^cart/add/wine/(?P<level>\w+)/$', 'cart_add_wine', name='cart_add_wine'),
    url(r'^cart/add/tasting/kit/$', 'cart_add_tasting_kit', name='cart_add_tasting_kit'),
    url(r'^cart/remove/(?P<cart_id>\d+)/(?P<item_id>\d+)/$', 'cart_remove_item', name='cart_remove_item'),
    url(r'^cart/$', 'cart', name='cart'),
    url(r'^cart/customize/$', 'customize_checkout', name='customize_checkout'),
    url(r'^order/place/$', 'place_order', name='place_order'),
    url(r'^order/complete/(?P<order_id>[\-\w]+)/$', 'order_complete', name='order_complete'),
    url(r'^order/history/$', 'order_history', name='order_history'),

    url(r'^edit/credit/$', 'edit_credit_card', name='edit_credit_card'),
    url(r'^edit/shipping/$', 'edit_shipping_address', name='edit_shipping_address'),

    url(r'^supplier/party/list/$', 'supplier_party_list', name='supplier_party_list'),
    url(r'^supplier/party/orders/(?P<party_id>\d+)/$', 'supplier_party_orders', name='supplier_party_orders'),
    url(r'^supplier/orders/pending/$', 'supplier_pending_orders', name='supplier_pending_orders'),
    url(r'^supplier/orders/fulfilled/$', 'supplier_fulfilled_orders', name='supplier_fulfilled_orders'),
    url(r'^supplier/orders/all/$', 'supplier_all_orders', name='supplier_all_orders'),
    url(r'^supplier/edit/order/(?P<order_id>[\-\w]+)/$', 'supplier_edit_order', name='supplier_edit_order'),

    # access error pages
    url(r'^suppliers/only/$', 'suppliers_only', name='suppliers_only'),
    url(r'^pros/only/$', 'pros_only', name='pros_only'),
)
