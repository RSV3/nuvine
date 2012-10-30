from django.conf.urls import patterns, url

from accounts.forms import VinelyEmailAuthenticationForm

urlpatterns = patterns('',

  #  url(r'^login/$', 'django.contrib.auth.views.login',
  #    {'authentication_form': EmailAuthenticationForm, 'template_name': 'email_usernames/login.html'}, name='login'),
  url(r'^login/$', 'django.contrib.auth.views.login',
     {'authentication_form': VinelyEmailAuthenticationForm}, name='login'),
  # url(r'^login/$', 'accounts.views.login',
  #    {'authentication_form': VinelyEmailAuthenticationForm}, name='login'),
  url(r'^my/information/$', 'accounts.views.my_information', name='my_information'),
  url(r'^edit/subscription/$', 'accounts.views.edit_subscription', name='edit_subscription'),
  url(r'^change/password/$', 'accounts.views.change_password', name='change_password'),
  url(r'^verify/eligibility/$', 'accounts.views.verify_eligibility', name='verify_eligibility'),
  url(r'^forgot/password/$', 'accounts.views.forgot_password', name='forgot_password'),
  url(r'^profile/$', 'accounts.views.profile', name='accounts_profile'),
  url(r'^signup/(?P<account_type>\d+)/$', 'accounts.views.sign_up', name='sign_up'),
  url(r'^verify/(?P<verification_code>[\-\w]{36})/$', 'accounts.views.verify_account', name='verify_account'),
  url(r'^verify/email/(?P<verification_code>[\-\w]{36})/$', 'accounts.views.verify_email', name='verify_email'),
  url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
  url(r'^terms/$', 'accounts.views.terms', name="terms"),
  url(r'^privacy/$', 'accounts.views.privacy', name='privacy'),
  url(r'^make/(?P<account_type>\w+)/$', 'accounts.views.make_pro_host', name='make_pro_host'),
)
