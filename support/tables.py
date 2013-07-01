from django_tables2 import tables
from django_tables2 import columns
from django_tables2.utils import A
from django_tables2 import Attrs
from support.models import WineInventory, TastingKitInventory
from main.models import Order
from accounts.models import User


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


class UserTable(tables.Table):
  name = columns.TemplateColumn('<a href="{% url support:view_user_details record.id %}">{{ record.first_name }} {{ record.last_name }}</a>', verbose_name='Name', accessor='id')
  phone = columns.Column(accessor='userprofile.phone')
  pro = columns.Column(accessor='userprofile.current_pro')

  class Meta:
    model = User
    fields = ('name', 'email', 'phone', 'pro')
    attrs = {"class": "paleblue table table-striped"}


class OrderHistoryTable(tables.Table):
  vinely_order_id = columns.LinkColumn('order_complete', args=[A('order_id')], order_by=('id'))
  order_date = columns.TemplateColumn('{{ record.order_date|date:"F j, o" }}', order_by=('order_date'))
  receiver = columns.Column(verbose_name='Ordered For', order_by=('receiver.first_name', 'receiver.last_name'))
  order_total = columns.Column(verbose_name='Order Total', accessor='cart.total')
  # fulfill_status = columns.Column(verbose_name='Order Status')

  class Meta:
    model = Order
    attrs = {'class': 'table table-striped'}
    fields = ('vinely_order_id', 'order_date', 'receiver', 'order_total', 'fulfill_status')

  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user')
    super(OrderHistoryTable, self).__init__(*args, **kwargs)

  def render_receiver(self, record, column):
    if self.user == record.receiver:
      return "Myself"
    if record.receiver.first_name:
      return "%s %s" % (record.receiver.first_name, record.receiver.last_name)
    else:
      return "Anonymous"


class PartyTable(tables.Table):
  title = columns.LinkColumn('support:view_party_detail', args=[A('id')])

  class Meta:
    model = User
    fields = ('title', 'event_date', 'host', 'pro', 'kit_ordered')
    attrs = {"class": "paleblue table table-striped"}
