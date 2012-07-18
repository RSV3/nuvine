from django import forms
from accounts.models import Address, UserProfile
from django.contrib.auth.models import User

class ChangePasswordForm(forms.Form):
  email = forms.CharField(widget=forms.HiddenInput)
  old_password = forms.CharField(max_length=64, widget=forms.PasswordInput)
  new_password = forms.CharField(max_length=64, widget=forms.PasswordInput)
  retype_password = forms.CharField(max_length=64, widget=forms.PasswordInput)

  def clean(self):
    cleaned_data = super(ChangePasswordForm, self).clean()

    # need to first check the temporary password
    u = User.objects.get(email=cleaned_data['email'])
    if not u.check_password(cleaned_data['old_password']):
      raise forms.ValidationError('Your old password does not match')

    # verify the two passwords are equal and not same as temporary password
    if cleaned_data['new_password'] != cleaned_data['retype_password']:
      raise forms.ValidationError('The new passwords do not match.  Please re-verify your new password')

    return cleaned_data


class VerifyAccountForm(forms.Form):
  email = forms.CharField(widget=forms.HiddenInput)
  temp_password = forms.CharField(label="Temporary Password", max_length=64, widget=forms.PasswordInput)
  new_password = forms.CharField(max_length=64, widget=forms.PasswordInput)
  retype_password = forms.CharField(max_length=64, widget=forms.PasswordInput)

  def clean(self):
    cleaned_data = super(VerifyAccountForm, self).clean()

    try:
      # need to first check the temporary password
      u = User.objects.get(email=cleaned_data['email'])
      if not u.check_password(cleaned_data['temp_password']):
        raise forms.ValidationError('Your temporary password does not match')
    except User.DoesNotExist:
      raise forms.ValidationError('You should sign up first')

    # verify the two passwords are equal and not same as temporary password
    if cleaned_data['new_password'] != cleaned_data['retype_password']:
      raise forms.ValidationError('The new passwords do not match.  Please re-verify your new password')

    return cleaned_data

class VerifyEligibilityForm(forms.ModelForm):

  class Meta:
    model = UserProfile

  def __init__(self, *args, **kwargs):
    super(VerifyEligibilityForm, self).__init__(*args, **kwargs)
    self.fields['dob'].widget.attrs['class'] = 'datepicker'
    self.fields['user'].widget = forms.HiddenInput()

  """
  user = models.OneToOneField(User)

  dob = models.DateField(null=True, blank=True)
  # drivers license number
  dl_number = models.CharField(max_length=32, null=True, blank=True)
  phone = models.CharField(max_length=16, null=True, blank=True)
  accepted_tos = models.BooleanField(default=False)
  age = models.IntegerField(default=0)
  above_21 = models.BooleanField(default=False)
  wine_personality = models.ForeignKey(WinePersonality, null=True, blank=True)

  billing_address = models.ForeignKey(Address, null=True, related_name="billed_to")
  shipping_address = models.ForeignKey(Address, null=True, related_name="shipped_to")
  credit_cards = models.ManyToManyField(CreditCard)

  party_addresses = models.ManyToManyField(Address)

  """

class UpdateAddressForm(forms.ModelForm):

  class Meta:
    model = Address 

  def __init__(self, *args, **kwargs):
    super(UpdateAddressForm, self).__init__(*args, **kwargs)


