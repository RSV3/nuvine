from django import forms
from django.contrib.auth.models import User, Group
from emailusernames.utils import create_user, create_superuser

from main.models import ContactRequest

class ContactRequestForm(forms.ModelForm):

  class Meta:
    model = ContactRequest


