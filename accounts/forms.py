from django import forms
from django.contrib.auth.models import User
from django.contrib.localflavor.us import forms as us_forms

from emailusernames.forms import EmailUserChangeForm

from accounts.models import Address, UserProfile, CreditCard, SubscriptionInfo
from main.models import LineItem
from creditcard.fields import *



class UserInfoForm(EmailUserChangeForm):

  class Meta:
    model = User
    exclude = ['last_login', 'groups', 'date_joined', 'is_active', 'is_staff', 'is_superuser']

class ImagePhoneForm(forms.ModelForm):

  class Meta:
    model = UserProfile
    fields = ['image', 'phone']

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
    exclude = ['wine_personality', 'prequestionnaire', 'billing_address', 'shipping_address',
              'credit_card', 'credit_cards', 'party_addresses', 'shipping_addresses']

  def __init__(self, *args, **kwargs):
    super(VerifyEligibilityForm, self).__init__(*args, **kwargs)
    self.fields['dob'].widget.attrs['class'] = 'datepicker'
    self.fields['user'].widget = forms.HiddenInput()

class UpdateAddressForm(forms.ModelForm):

  class Meta:
    model = Address 

  def __init__(self, *args, **kwargs):
    super(UpdateAddressForm, self).__init__(*args, **kwargs)


class ForgotPasswordForm(forms.Form):

  email = forms.EmailField()

  def clean_email(self):
    try:
      u = User.objects.get(email=self.cleaned_data['email'])
    except User.DoesNotExist:
      raise forms.ValidationError('User with %s does not exist'%(self.cleaned_data['email']))

    return self.cleaned_data['email']


class CreditCardForm(forms.ModelForm):
  """
    This form is not used 
  """
  card_number = CreditCardField(required=True)
  expiry_date = ExpiryDateField(required=True)
  verification_code = VerificationValueField(required=True)
  billing_zipcode = us_forms.USZipCodeField()
  #save_card = forms.BooleanField(label="Save this card in My Account", required=False) 

  class Meta:
    model = CreditCard

class PaymentForm(forms.ModelForm):
  """
    This form is used
  """
  card_number = CreditCardField(required = True, label = "Card Number")
  exp_month = forms.ChoiceField(required=True, choices=[(x, x) for x in xrange(1, 13)])
  exp_year = forms.ChoiceField(required=True, choices=[(x, x) for x in xrange(date.today().year, date.today().year + 15)])
  verification_code = forms.IntegerField(required = True, label = "CVV Number",
      max_value = 9999, widget = forms.TextInput(attrs={'size': '4'}))
  billing_zipcode = us_forms.USZipCodeField()
  #save_card = forms.BooleanField(label="Save this card in My Account", required=False) 

  class Meta:
    model = CreditCard

  def __init__(self, *args, **kwargs):
    self.payment_data = kwargs.pop('payment_data', None)
    super(PaymentForm, self).__init__(*args, **kwargs)
    self.fields['verification_code'].widget = forms.PasswordInput()
    self.fields['card_type'].widget = forms.HiddenInput()
 
  def clean(self):
    cleaned_data = super(PaymentForm, self).clean()

    if 'card_number' in cleaned_data:
      cleaned_data['card_type'] = self.fields['card_number'].get_cc_type(cleaned_data['card_number'])

    exp_month = cleaned_data.get('exp_month')
    exp_year = cleaned_data.get('exp_year')

    if exp_year in forms.fields.EMPTY_VALUES:
      #raise forms.ValidationError("You must select a valid Expiration year.")
      self._errors["exp_year"] = self.error_class(["You must select a valid Expiration year."])
      if exp_year:
        del cleaned_data["exp_year"]
    if exp_month in forms.fields.EMPTY_VALUES:
      #raise forms.ValidationError("You must select a valid Expiration month.")
      self._errors["exp_month"] = self.error_class(["You must select a valid Expiration month."])
      if exp_month:
        del cleaned_data["exp_month"]

    if exp_year and exp_month:    
      year = int(exp_year)
      month = int(exp_month)
      # find last day of the month
      day = monthrange(year, month)[1]
      expire = date(year, month, day)
   
      if date.today() > expire:
        #raise forms.ValidationError("The expiration date you entered is in the past.")
        self._errors["exp_year"] = self.error_class(["The expiration date you entered is in the past."])
    else:
        self._errors["exp_year"] = self.error_class(["Is it full 4-digit year you specified?"])
   
    return cleaned_data

  def save(self, commit=True, force_insert=False, force_update=False, *args, **kwargs):
    m = super(PaymentForm, self).save(commit=False, *args, **kwargs)

    # encrypt card number
    m.encrypt_card_num(self.cleaned_data['card_number'])
    m.encrypt_cvv(self.cleaned_data['verification_code'])

    if commit:
      m.save()
    return m

class UpdateSubscriptionForm(forms.ModelForm):

  class Meta:
    model = SubscriptionInfo

  def __init__(self, *args, **kwargs):
    super(UpdateSubscriptionForm, self).__init__(*args, **kwargs)
    self.fields['user'].widget = forms.HiddenInput()


from emailusernames.forms import NameEmailUserCreationForm
class NameEmailUserMentorCreationForm(NameEmailUserCreationForm):
  mentor = forms.EmailField(required=False, label="Vinely Pro Mentor")
    
