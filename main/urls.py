from django.conf.urls import patterns, include, url

urlpatterns = patterns('main.views',
    url(r'^home/$', 'home', name='home_page'),
    url(r'^about/$', 'about', name='about'),
    url(r'^contact/$', 'contact_us', name='contact_us'),
)
