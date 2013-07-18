from django.conf.urls import patterns, url

urlpatterns = patterns('api_logger.views',
    url(r'^$', 'log', name='log'),
    url(r'^(?P<log_id>\d+)/$', 'log_detail', name='log_detail'),
    url(r'^cleanup/$', 'log_cleanup', name='log_cleanup'),
)
