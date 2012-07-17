from django import forms
from accounts.models import Address, UserProfile

class ChangePasswordForm(forms.Form):
  old_password = forms.CharField(max_length=64, widget=forms.PasswordInput)
  new_password = forms.CharField(max_length=64, widget=forms.PasswordInput)
  retype_password = forms.CharField(max_length=64, widget=forms.PasswordInput)

class VerifyAccountForm(forms.Form):
  temp_password = forms.CharField(label="Temporary Password", max_length=64, widget=forms.PasswordInput)
  new_password = forms.CharField(max_length=64, widget=forms.PasswordInput)
  retype_password = forms.CharField(max_length=64, widget=forms.PasswordInput)

  def clean(self):
    cleaned_data = super(VerifyAccountForm, self).clean()

    # TODO: need to first check the temporary password

    # TODO: verify the two passwords are equal and not same as temporary password

    return cleaned_data

class ApprovalApplication(forms.ModelForm):

  class Meta:
    model = UserProfile

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
