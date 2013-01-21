from django_tables2 import tables
from support.models import WineInventory


class WineInventoryTable(tables.Table):

  class Meta:
    model = WineInventory
    attrs = {"class": "paleblue table table-striped"}
