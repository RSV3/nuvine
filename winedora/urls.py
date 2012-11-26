from django.conf.urls import patterns, include, url
from emailusernames.forms import EmailAuthenticationForm
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'winedora.views.home', name='home'),
    # url(r'^winedora/', include('winedora.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'winedora.views.home', name='landing_page'),
    url(r'^', include('main.urls')),
    url(r'^personality/', include('personality.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^support/', include('support.urls', namespace="support")),
    url(r'^social/', include('social.urls')),
    url(r'^cms/', include('cms.urls', namespace="cms")),
    url(r'^stripe/', include('stripecard.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + staticfiles_urlpatterns() 
