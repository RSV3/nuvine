
import django_tables2 as tables
from django_tables2 import Attrs
from django_tables2.utils import A
from api_logger.models import APILog


table_attrs = Attrs({'class': 'table table-striped'})


class APILogTable(tables.Table):
    id = tables.LinkColumn('api_logger:log_detail', args=[A('pk')])
    request_data = tables.TemplateColumn('<a href="{{ record.get_absolute_url }}">{{ record.request_data|truncatechars:25 }}</a>')
    response_data = tables.TemplateColumn('<a href="{{ record.get_absolute_url }}">{{ record.response_data|truncatechars:25 }}</a>')

    class Meta:
        model = APILog
        attrs = table_attrs
