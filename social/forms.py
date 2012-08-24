from django import forms

class XOAuthForm(forms.Form):

  user = forms.CharField(max_length=64)
  token = forms.CharField(max_length=128)
  secret = forms.CharField(max_length=128)