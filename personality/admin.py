from django.contrib import admin
from django.contrib.auth.models import User
from personality.models import WineRatingData
from personality.utils import calculate_wine_personality


def recalculate_personality(modeladmin, request, queryset):
  for obj in queryset.values('user').distinct():
    user_id = obj['user']
    user = User.objects.get(id=user_id)
    wine1 = WineRatingData.objects.get(user=user, wine__id=1)
    wine2 = WineRatingData.objects.get(user=user, wine__id=2)
    wine3 = WineRatingData.objects.get(user=user, wine__id=3)
    wine4 = WineRatingData.objects.get(user=user, wine__id=4)
    wine5 = WineRatingData.objects.get(user=user, wine__id=5)
    wine6 = WineRatingData.objects.get(user=user, wine__id=6)

    calculate_wine_personality(user, wine1, wine2, wine3, wine4, wine5, wine6)

recalculate_personality.short_description = "Recalculate personality"

class WineRatingDataAdmin(admin.ModelAdmin):

  list_display = ('user_email', 'wine_num', 'overall', 'personality'  ) 
  list_editable = ('overall',)
  actions = [recalculate_personality] 

  def user_email(self, instance):
    return instance.user.email

  def wine_num(self, instance):
    return instance.wine.id

  def personality(self, instance):
    return instance.user.get_profile().wine_personality


admin.site.register(WineRatingData, WineRatingDataAdmin)