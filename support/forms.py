from django import forms
from django.db.models import Q

from support.models import InventoryUpload
from main.models import SelectedWine
from personality.models import WineRatingData, Wine

class InventoryUploadForm(forms.ModelForm):

  class Meta:
    model = InventoryUpload
    exclude = ['created']


class SelectedWineRatingForm(forms.ModelForm):
  """
    Used to rate the wines that have been shipped and consumed
  """
  record_id = forms.IntegerField(required=False)

  class Meta:
    model = SelectedWine

  def __init__(self, *args, **kwargs):
    super(SelectedWineRatingForm, self).__init__(*args, **kwargs)
    self.fields['record_id'].widget = forms.HiddenInput()
    self.fields['order'].widget = forms.HiddenInput()
    self.fields['wine'].widget = forms.HiddenInput()
    #self.fields['wine'].widget = forms.TextInput()
    #self.fields['wine'].widget.attrs['disabled'] = True
    if 'wine_name' in self.initial:
      self.fields['wine'].label = self.initial['wine_name']
    self.fields['overall_rating'].widget = forms.RadioSelect(choices=WineRatingData.LIKENESS_CHOICES)
    self.fields['overall_rating'].widget.attrs['class'] = "inline-radio"


class SelectWineForm(forms.ModelForm):
  """
    Used to manually fulfill wine for an order

    Very hacky.
  """
  record_id = forms.IntegerField(required=False)

  class Meta:
    model = SelectedWine
    exclude = ['order', 'overall_rating']

  def __init__(self, *args, **kwargs):
    super(SelectWineForm, self).__init__(*args, **kwargs)
    self.fields['record_id'].widget = forms.HiddenInput()

    if 'wine' in self.initial:
      # this is needed to cover the case where a wine is already selected and inventory is 0
      # we still need to show the wine selected
      wines = Wine.objects.filter(Q(is_taste_kit_wine=False, wineinventory__on_hand__gt=0) | Q(id=self.initial['wine']))
    else:
      # used to show list of all wines that are in inventory
      wines = Wine.objects.filter(is_taste_kit_wine=False, wineinventory__on_hand__gt=0)

    # in order filter the qualified wines by one's personal preferences
    if 'color_filter' in self.initial:
      print self.initial['color_filter']
      wines = wines.filter(color=self.initial['color_filter'])
    if 'sparkling_filter' in self.initial:
      if not self.initial['sparkling_filter']:
        wines = wines.filter(sparkling=self.initial['sparkling_filter'])
    if 'category_filter' in self.initial:
      wines = wines.filter(vinely_category__in=self.initial['category_filter'])

    self.fields['wine'].queryset = wines

