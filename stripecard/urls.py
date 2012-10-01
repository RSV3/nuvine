from django.conf.urls import patterns, include, url
# from stripecard.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    'stripecard.views',
    url(r'^webhooks/$', 'webhooks', name="webhooks"),
)