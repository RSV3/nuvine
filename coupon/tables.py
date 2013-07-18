
import django_tables2 as tables
from django_tables2 import Attrs
from django_tables2.utils import A
from coupon.models import Coupon


table_attrs = Attrs({'class': 'table table-striped'})


class CouponTable(tables.Table):
  name = tables.LinkColumn('coupon_create', args=[A('pk')])
  active = tables.TemplateColumn('{% if record.active %}<i class="icon-ok"></i>{% endif %}')
  discount = tables.TemplateColumn('{% if record.amount_off %}${{ record.amount_off }}{% else %}{{ record.percent_off }}%{% endif %}')

  class Meta:
    model = Coupon
    attrs = table_attrs
    fields = ('name', 'code', 'discount', 'active', 'times_redeemed', 'max_redemptions')
