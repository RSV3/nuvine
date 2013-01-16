from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.localflavor.us import forms as us_forms

import string
from lepl.apps.rfc3696 import Email

from support.models import InventoryUpload


class InventoryUploadForm(forms.ModelForm):

  class Meta:
    model = InventoryUpload
    exclude = ['created']

