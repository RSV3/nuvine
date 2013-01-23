from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.localflavor.us import forms as us_forms
from django.contrib.admin import widgets

import string
from lepl.apps.rfc3696 import Email

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
    self.fields['wine'].widget = forms.HiddenInput()
    self.fields['overall_rating'].widget = forms.RadioSelect(choices=WineRatingData.LIKENESS_CHOICES)


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
