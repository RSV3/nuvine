from django.conf.urls import patterns, url
from landing import views

urlpatterns = patterns('',
    url(r'^$', views.hello_world, name='index'),
    url(r'^invite/$', views.invite, name='invite'),
)