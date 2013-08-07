
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django_tables2 import RequestConfig

from api_logger.tables import APILogTable
from api_logger.models import APILog

import json


@login_required
def log(request):
    data = {}
    log = APILog.objects.all().order_by('-id')
    table = APILogTable(log)
    RequestConfig(request).configure(table)
    data['table'] = table
    return render(request, 'api_logger/log.html',  data)


@login_required
def log_detail(request, log_id):
    log = get_object_or_404(APILog, pk=log_id)

    data = {
        'request_data': log.request_data,
        'response_data': log.response_data
    }
    data = json.dumps(data)
    return HttpResponse(data, mimetype="application/json")


@login_required
def log_cleanup(request):
    # cleanup old logs and leave only last 20
    logs = APILog.objects.all().order_by('-id')[:20]
    APILog.objects.exclude(id__in=logs).delete()
    return HttpResponseRedirect(reverse('api_logger:log'))
