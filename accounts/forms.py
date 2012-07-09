from django import forms

class ChangePasswordForm(forms.Form):
  old_password = forms.CharField(max_length=64)
  new_password = forms.CharField(max_length=64)
  retype_password = forms.CharField(max_length=64)

class VerifyAccountForm(forms.Form):
  temp_password = forms.CharField(verbose_name="Temporary Password", max_length=64)
  new_password = forms.CharField(max_length=64)
  retype_password = forms.CharField(max_length=64)


