from django_tables2 import tables
from django_tables2 import columns
from django_tables2.utils import A
from support.models import WineInventory
from main.models import Order


class WineInventoryTable(tables.Table):
  sku = columns.Column(accessor='wine.sku')
  wine = columns.Column(order_by=('wine__name'))

  class Meta:
    model = WineInventory
    fields = ('sku', 'wine', 'on_hand', 'updated',)
    order_by = ['sku']
    attrs = {"class": "paleblue table table-striped"}


class OrderTable(tables.Table):

  vinely_order_id = columns.LinkColumn("support:edit_order", args=[A('pk')], verbose_name="Order ID", order_by=('id',))
  receiver_info = columns.Column(verbose_name="Ordered By", order_by=('receiver.first_name', 'receiver.last_name', 'receiver.email',))
  slot_summary = columns.Column(verbose_name="# Slots [Selected]", order_by=('slots_filled',))

  class Meta:
    model = Order
    fields = ("vinely_order_id", "receiver_info", "order_date", "slot_summary", "fulfill_status", )
    attrs = {"class": "paleblue table table-striped"}


class PastOrderTable(tables.Table):

  vinely_order_id = columns.LinkColumn("support:view_past_orders", args=[A('pk')], verbose_name="Order ID", order_by=('id',))
  receiver_info = columns.Column(verbose_name="Ordered By", order_by=('receiver.first_name', 'receiver.last_name', 'receiver.email',))
  slot_summary = columns.Column(verbose_name="# Slots [Selected]", order_by=('slots_filled',))

  class Meta:
    model = Order
    fields = ("vinely_order_id", "receiver_info", "order_date", "slot_summary", "fulfill_status", )
    attrs = {"class": "paleblue table table-striped"}
