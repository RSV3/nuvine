from django.conf.urls import patterns, include, url

urlpatterns = patterns('cms.views',
    url(r'^list/$', 'template_list', name='list_templates'),
    url(r'^list/(?P<type>\d)/$', 'template_list', name='template_list'),
    url(r'^edit/template/(?P<key>\w+)/$', 'edit_template', name='edit_template'),

)