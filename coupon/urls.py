from django.conf.urls import patterns, url

urlpatterns = patterns('coupon.views',
    url(r'^$', 'coupon_list', name="coupon_list"),
    url(r'^list/$', 'coupon_list', name="coupon_list"),
    url(r'^add/$', 'coupon_create', name="coupon_create"),
    url(r'^edit/(?P<coupon_id>\d+)/$', 'coupon_create', name="coupon_create"),
)
