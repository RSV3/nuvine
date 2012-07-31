from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse

from emailusernames.forms import EmailAuthenticationForm

urlpatterns = patterns('',

  #  url(r'^login/$', 'django.contrib.auth.views.login',
  #    {'authentication_form': EmailAuthenticationForm, 'template_name': 'email_usernames/login.html'}, name='login'),
  url(r'^login/$', 'django.contrib.auth.views.login',
     {'authentication_form': EmailAuthenticationForm}, name='login'),

  url(r'^change/password/$', 'accounts.views.change_password', name='change_password'),
  url(r'^verify/eligibility/$', 'accounts.views.verify_eligibility', name='verify_eligibility'),
  url(r'^update/addresses/$', 'accounts.views.update_addresses', name='update_addresses'),
  url(r'^profile/$', 'accounts.views.profile', name='accounts_profile'),
  url(r'^settings/$', 'accounts.views.settings', name='accounts_settings'),
  url(r'^signup/(?P<account_type>\d+)/$', 'accounts.views.sign_up', name='sign_up'),
  url(r'^verify/(?P<verification_code>[\-\w]{36})/$', 'accounts.views.verify_account', name='verify_account'),
  url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
  url(r'^questionnaire/pre/$', 'accounts.views.pre_questionnaire', name='pre_questionnaire'),
)

