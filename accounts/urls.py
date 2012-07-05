from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse

from emailusernames.forms import EmailAuthenticationForm

urlpatterns = patterns('',

  #  url(r'^login/$', 'django.contrib.auth.views.login',
  #    {'authentication_form': EmailAuthenticationForm, 'template_name': 'email_usernames/login.html'}, name='login'),
  url(r'^login/$', 'django.contrib.auth.views.login',
     {'authentication_form': EmailAuthenticationForm}, name='login'),

  url(r'^profile/$', 'accounts.views.profile', name='accounts_profile'),
  url(r'^settings/$', 'accounts.views.settings', name='accounts_settings'),
  url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
)

