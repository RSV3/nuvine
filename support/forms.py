from django import forms

from support.models import InventoryUpload
from main.models import SelectedWine
from personality.models import WineRatingData


class InventoryUploadForm(forms.ModelForm):

  class Meta:
    model = InventoryUpload
    exclude = ['created']


class SelectedWineRatingForm(forms.ModelForm):
  """
    Used to rate the wines that have been shipped and consumed
  """

  class Meta:
    model = SelectedWine

  def __init__(self, *args, **kwargs):
    super(SelectedWineRatingForm, self).__init__(*args, **kwargs)
    self.fields['order'].widget = forms.HiddenInput()
    self.fields['wine'].widget = forms.TextInput()
    self.fields['wine'].widget.attrs['disabled'] = True
    self.fields['overall_rating'].widget = forms.RadioSelect(choices=WineRatingData.LIKENESS_CHOICES)
    self.fields['overall_rating'].widget.attrs['class'] = "inline-radio"


class SelectWineForm(forms.ModelForm):
  """
    Used to manually fulfill wine for an order
  """
  record_id = forms.IntegerField(required=False)

  class Meta:
    model = SelectedWine
    exclude = ['order', 'overall_rating']

  def __init__(self, *args, **kwargs):
    super(SelectWineForm, self).__init__(*args, **kwargs)
    self.fields['record_id'].widget = forms.HiddenInput()
