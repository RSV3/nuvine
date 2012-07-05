from django import forms
from main.models import ContactRequest

class ContactRequestForm(forms.ModelForm):

  class Meta:
    model = ContactRequest
