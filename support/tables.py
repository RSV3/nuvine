from django_tables2 import tables
from django_tables2 import columns
from django_tables2.utils import A
from django_tables2 import Attrs
from support.models import WineInventory, TastingKitInventory
from main.models import Order


class WineInventoryTable(tables.Table):
  sku = columns.Column(accessor='wine.sku')
  wine = columns.Column(order_by=('wine__name'))

  class Meta:
    model = WineInventory
    fields = ('sku', 'wine', 'on_hand', 'updated',)
    order_by = ['sku']
    attrs = {"class": "paleblue table table-striped"}


class TastingInventoryTable(tables.Table):
  sku = columns.Column(accessor='tasting_kit.sku')
  tasting_kit = columns.Column(order_by=('tasting_kit__name'))

  class Meta:
    model = TastingKitInventory
    fields = ('sku', 'tasting_kit', 'on_hand', 'updated',)
    order_by = ['sku']
    attrs = {"class": "paleblue table table-striped"}


class OrderTable(tables.Table):
  orders = columns.CheckBoxColumn(Attrs({'name': 'orders', 'td__input': {'class': 'order'}, 'th__input': {'class': 'all-orders'}}), accessor='id')
  vinely_order_id = columns.LinkColumn("support:edit_order", args=[A('pk')], verbose_name="Order ID", order_by=('id',))
  receiver_info = columns.Column(verbose_name="Ordered By", order_by=('receiver.first_name', 'receiver.last_name', 'receiver.email',))
  # slot_summary = columns.Column(verbose_name="# Slots [Selected]", orderable=False)  # order_by=('filled_slots',))

  class Meta:
    model = Order
    fields = ("orders", "vinely_order_id", "receiver_info", "order_date", "fulfill_status", )
    attrs = {"class": "paleblue table table-striped"}
    order_by = ['-vinely_order_id']


class PastOrderTable(tables.Table):

  vinely_order_id = columns.LinkColumn("support:view_past_orders", args=[A('pk')], verbose_name="Order ID", order_by=('id',))
  receiver_info = columns.Column(verbose_name="Ordered By", order_by=('receiver.first_name', 'receiver.last_name', 'receiver.email',))
  # slot_summary = columns.Column(verbose_name="# Slots [Selected]", orderable=False)  # order_by=('filled_slots',))

  class Meta:
    model = Order
    fields = ("vinely_order_id", "receiver_info", "order_date", "fulfill_status", )
    attrs = {"class": "paleblue table table-striped"}
