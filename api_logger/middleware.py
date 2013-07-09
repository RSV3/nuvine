
from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings
from api_logger.models import APILog
# import json


class APILogMiddleWare(object):
    def __init__(self):
        # don't use this middleware in production
        # better to err on caution and assume production if setting not found
        if getattr(settings, 'DEPLOY', True):
            raise MiddlewareNotUsed

    def process_view(self, request, view_func, view_args, view_kwargs):
        # only interested in the api calls
        if not view_kwargs.get('api_name'):
            return

        post_data = {}
        if request.method in ['POST', 'PUT']:
            post_data = request.raw_post_data

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
        if x_forwarded_for:
            remote_addr = x_forwarded_for.split(',')[0].strip()
        else:
            remote_addr = request.META.get('REMOTE_ADDR', None)

        uri = request.META.get('PATH_INFO', '')
        api = APILog.objects.create(**{
            'user': request.user if request.user.is_authenticated() else None,
            'source': remote_addr,
            'method': request.method,
            'uri': uri,
            'request_data': post_data,
        })
        request.session['api_logger'] = api.pk

    def process_response(self, request, response):
        # only interested in the api calls
        # should fix this to be more generic
        if request.META.get('PATH_INFO').startswith('/api/v1/'):
            if hasattr(request, 'session'):
                api_pk = request.session.get('api_logger')
                try:
                    api = APILog.objects.get(pk=api_pk)
                    api.status = response.status_code
                    api.response_data = response.content
                    api.save()
                except:
                    pass
        return response
