from django.conf.urls import patterns, url

urlpatterns = patterns('cms.views',
    url(r'^$', 'template_list', name='template_list'),
    url(r'^list/$', 'template_list', name='template_list'),
    url(r'^list/(?P<type>\d)/$', 'template_list', name='template_list'),
    url(r'^edit/template/(?P<key>\w+)/$', 'edit_template', name='edit_template'),
)
