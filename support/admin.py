from django.contrib import admin
from support.models import WineInventory


class WineInventoryAdmin(admin.ModelAdmin):
  list_display = ('sku', 'wine', 'on_hand', 'updated')
  ordering = ['wine__sku', 'on_hand']

  def sku(self, instance):
    return instance.wine.sku

admin.site.register(WineInventory, WineInventoryAdmin)
