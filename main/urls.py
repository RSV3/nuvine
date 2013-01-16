from django.conf.urls import patterns, url

urlpatterns = patterns('main.views',
    url(r'^home/$', 'home', name='home_page'),
    url(r'^our_story/$', 'our_story', name='our_story'),
    # url(r'^get/started$', 'get_started', name='get_started'),
    url(r'^contact/$', 'contact_us', name='contact_us'),
    url(r'^howto/$', 'how_it_works', name='how_it_works'),
    url(r'^become/vip/$', 'become_vip', name='become_vip'),
    url(r'^dashboard/$', 'dashboard', name='dashboard'),
    url(r'^rate/wines/$', 'rate_wines', name='rate_wines'),
    url(r'^uncover/personality/$', 'uncover_personality', name='uncover_personality'),
    url(r'^resend/invite/$', 'resend_rsvp', name='resend_rsvp'),

    url(r'^host/party/$', 'host_vinely_party', name='host_vinely_party'),
    url(r'^host/list/(?P<host_name_email>[@\w\+\-\.]+)/$', 'party_host_list', name='party_host_list'),
    url(r'^taster/list/(?P<taster_name_email>[@\w\+\-\.]+)/$', 'my_taster_list', name='my_taster_list'),
    url(r'^user/info/(?P<user_email>[@\w\+\-\.]+)/$', 'party_user_info', name='party_user_info'),

    url(r'^party/list/$', 'party_list', name='party_list'),
    url(r'^party/select/$', 'party_select', name='party_select'),
    url(r'^party/add/(?P<party_pro>\w+)/$', 'party_add', name='party_add'),
    url(r'^party/add/$', 'party_add', name='party_add'),
    url(r'^party/add/(?P<party_id>\d+)/$', 'party_add', name='party_add'),
    # url(r'^party/taster/add/$', 'party_add_taster', name='party_add_taster'),
    url(r'^party/find/friends/(?P<party_id>\d+)/$', 'party_find_friends', name='party_find_friends'),
    url(r'^party/review/(?P<party_id>\d+)/$', 'party_review_request', name='party_review_request'),
    url(r'^party/cancel/$', 'party_cancel', name='party_cancel'),
    url(r'^party/edit/taster/(?P<invite_id>\d+)/$', 'party_edit_taster_info', name='party_edit_taster_info'),
    url(r'^party/edit/taster/(?P<invite_id>\d+)/(?P<change_rsvp>\w)/$', 'party_edit_taster_info', name='party_edit_taster_info'),
    url(r'^party/remove/taster/(?P<invite_id>\d+)/$', 'party_remove_taster', name='party_remove_taster'),
    url(r'^party/confirm/(?P<party_id>\d+)/$', 'party_confirm', name='party_confirm'),
    url(r'^party/details/(?P<party_id>\d+)/$', 'party_details', name='party_details'),
    url(r'^party/rsvp/(?P<party_id>\d+)/$', 'party_rsvp', name='party_rsvp'),
    url(r'^party/rsvp/(?P<party_id>\d+)/(?P<response>\d)/$', 'party_rsvp', name='party_rsvp'),
    url(r'^party/rsvp/(?P<rsvp_code>[\-\w]{36})/(?P<party_id>\d+)/$', 'party_rsvp', name='party_rsvp'),
    url(r'^party/rsvp/(?P<rsvp_code>[\-\w]{36})/(?P<party_id>\d+)/(?P<response>\d)/$', 'party_rsvp', name='party_rsvp'),
    url(r'^party/customize/invite/$', 'party_customize_invite', name='party_customize_invite'),
    url(r'^party/write/invitation/(?P<party_id>\d+)/$', 'party_write_invitation', name='party_write_invitation'),
    url(r'^party/preview/invitation/(?P<party_id>\d+)/$', 'party_preview_invitation', name='party_preview_invitation'),
    url(r'^party/send/invites/$', 'party_send_invites', name='party_send_invites'),
    # url(r'^party/taster/list/(?P<party_id>\d+)/$', 'party_taster_list', name='party_taster_list'),
    url(r'^party/taster/invite/(?P<party_id>\d+)/$', 'party_taster_invite', name='party_taster_invite'),
    url(r'^party/taster/invite/$', 'party_taster_invite', name='party_taster_invite'),
    url(r'^party/print/rating/(?P<party_id>\d+)/$', 'print_rating_cards', name='print_rating_cards'),
    url(r'^party/customize/thanks/note/$', 'party_customize_thanks_note', name='party_customize_thanks_note'),
    url(r'^party/send/thanks/note/$', 'party_send_thanks_note', name='party_send_thanks_note'),

    url(r'^order/start/$', 'start_order', name='start_order'),
    url(r'^order/start/(?P<receiver_id>\d+)/$', 'start_order', name='start_order'),
    url(r'^order/start/(?P<receiver_id>\d+)/(?P<party_id>\d+)/$', 'start_order', name='start_order'),
    url(r'^cart/add/wine/$', 'cart_add_wine', name='cart_add_wine'),
    # url(r'^cart/add/wine/(?P<level>\w+)/$', 'cart_add_wine', name='cart_add_wine'),
    #url(r'^cart/add/tasting/kit/$', 'cart_add_tasting_kit', name='cart_add_tasting_kit'),
    url(r'^cart/add/tasting/kit/(?P<party_id>\d+)/$', 'cart_add_tasting_kit', name='cart_add_tasting_kit'),
    url(r'^cart/remove/(?P<cart_id>\d+)/(?P<item_id>\d+)/$', 'cart_remove_item', name='cart_remove_item'),
    url(r'^cart/$', 'cart', name='cart'),
    url(r'^cart/customize/$', 'customize_checkout', name='customize_checkout'),
    url(r'^cart/tasting/kit/details/(?P<kit_id>\d+)/$', 'cart_kit_detail', name='cart_kit_detail'),
    url(r'^cart/wine/(?P<level>\w+)/(?P<quantity>\d+)/$', 'cart_quantity', name='cart_quantity'),

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
    url(r'^supplier/orders/history/$', 'supplier_order_history', name='supplier_order_history'),
    url(r'^supplier/wine/list/$', 'supplier_wine_list', name='supplier_wine_list'),
    url(r'^supplier/add/wine/$', 'supplier_add_wine', name='supplier_add_wine'),

    # access error pages
    url(r'^suppliers/only/$', 'suppliers_only', name='suppliers_only'),
    url(r'^pros/only/$', 'pros_only', name='pros_only'),
)

urlpatterns += patterns('main.views',
    url(r'^events/$', 'vinely_event', name='vinely_event'),
    url(r'^facebook/events/$', 'fb_vinely_event', name='fb_vinely_event'),
    url(r'^event/signup/(?P<party_id>\d+)/$', 'vinely_event_signup', name='vinely_event_signup'),
    url(r'^facebook/event/signup/(?P<party_id>\d+)/$', 'fb_vinely_event_signup', name='fb_vinely_event_signup'),
)
