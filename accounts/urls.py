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
  url(r'^card/delete/$', 'accounts.views.delete_card', name='delete_card'),
  url(r'^edit/subscription/$', 'accounts.views.edit_subscription', name='edit_subscription'),
  url(r'^cancel/subscription/$', 'accounts.views.cancel_subscription', name='cancel_subscription'),
  url(r'^change/password/$', 'accounts.views.change_password', name='change_password'),
  url(r'^verify/eligibility/$', 'accounts.views.verify_eligibility', name='verify_eligibility'),
  url(r'^forgot/password/$', 'accounts.views.forgot_password', name='forgot_password'),
  url(r'^activate/account/$', 'accounts.views.activate_account', name='activate_account'),
  url(r'^profile/$', 'accounts.views.profile', name='accounts_profile'),
  # url(r'^signup/(?P<account_type>\d+)/$', 'accounts.views.sign_up', name='sign_up'),
  url(r'^verify/(?P<verification_code>[\-\w]{36})/$', 'accounts.views.verify_account', name='verify_account'),
  url(r'^verify/email/(?P<verification_code>[\-\w]{36})/$', 'accounts.views.verify_email', name='verify_email'),
  url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
  # url(r'^logout/$', 'accounts.views.logout', name='logout'),
  url(r'^terms/$', 'accounts.views.terms', name="terms"),
  url(r'^privacy/$', 'accounts.views.privacy', name='privacy'),
  # url(r'^make/(?P<account_type>\w+)/$', 'accounts.views.make_pro_host', name='make_pro_host'),
  url(r'^make/host/$', 'accounts.views.make_host', name='make_host'),
  url(r'^make/host/(?P<state>\w+)/$', 'accounts.views.make_host', name='make_host'),
  url(r'^make/pro/$', 'accounts.views.make_pro', name='make_pro'),
  url(r'^make/pro/(?P<state>\w+)/$', 'accounts.views.make_pro', name='make_pro'),
  url(r'^make/taster/(?P<rsvp_code>[\-\w]{36})/$', 'accounts.views.make_taster', name='make_taster'),
  url(r'^unlink/pro/$', 'accounts.views.pro_unlink', name='pro_unlink'),
  url(r'^unlink/host/$', 'accounts.views.host_unlink', name='host_unlink'),
  url(r'^link/pro/$', 'accounts.views.pro_link', name='pro_link'),

  url(r'^join/club/$', 'accounts.views.join_club_start', name='join_club_start'),
  url(r'^join/club/hi/(?P<state>\w+)/$', 'accounts.views.join_club_start', name='join_club_start'),
  url(r'^join/club/signup/$', 'accounts.views.join_club_signup', name='join_club_signup'),
  url(r'^join/club/shipping/$', 'accounts.views.join_club_shipping', name='join_club_shipping'),
  url(r'^join/club/review/$', 'accounts.views.join_club_review', name='join_club_review'),
  url(r'^join/club/done/(?P<order_id>[\-\w]+)/$', 'accounts.views.join_club_done', name='join_club_done'),

  # test
  url(r'^my/information/test/$', 'accounts.views.fix_my_picture', name='fix_my_picture'),
)
