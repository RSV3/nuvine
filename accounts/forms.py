from django import forms
from django.contrib.auth.models import User
from django.contrib.localflavor.us import forms as us_forms

from emailusernames.forms import EmailUserChangeForm

from accounts.models import Address, UserProfile, CreditCard, SubscriptionInfo
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
  temp_password = forms.CharField(label="Temporary Password (from e-mail)", max_length=64, widget=forms.PasswordInput)
  new_password = forms.CharField(max_length=64, widget=forms.PasswordInput)
  retype_password = forms.CharField(max_length=64, widget=forms.PasswordInput)
  accepted_tos = forms.BooleanField(label="I accept the terms of service")

  def clean(self):
    cleaned_data = super(VerifyAccountForm, self).clean()

    try:
      # need to first check the temporary password
      u = User.objects.get(email=cleaned_data['email'])
      if not u.check_password(cleaned_data['temp_password']):
        raise forms.ValidationError('Your temporary password does not match')
    except User.DoesNotExist:
      raise forms.ValidationError('You should sign up first')
    except KeyError:
      raise forms.ValidationError('Please enter the temporary password from the e-mail you received from Vinely')

    # verify the two passwords are equal and not same as temporary password
    if cleaned_data['new_password'] != cleaned_data['retype_password']:
      raise forms.ValidationError('The new passwords do not match.  Please re-verify your new password.')

    return cleaned_data

from main.utils import UTC
from datetime import datetime, timedelta
import math

class VerifyEligibilityForm(forms.ModelForm):

  class Meta:
    model = UserProfile
    exclude = ['wine_personality', 'prequestionnaire', 'billing_address', 'shipping_address',
              'credit_card', 'credit_cards', 'party_addresses', 'shipping_addresses']

  def __init__(self, *args, **kwargs):
    super(VerifyEligibilityForm, self).__init__(*args, **kwargs)
    self.fields['dob'].widget.attrs['class'] = 'datepicker'
    self.fields['dob'].widget.attrs['placeholder'] = 'mm/dd/yyyy'
    self.fields['user'].widget = forms.HiddenInput()

  def clean(self):
    data = super(VerifyEligibilityForm, self).clean()
    dob = data['dob']

    if dob:
      today = datetime.date(datetime.now(tz=UTC()))
      datediff = today - dob
      if (datediff.days < timedelta(math.ceil(365.25 * 21)).days and data['above_21']) or (not dob and data['above_21']):
        raise forms.ValidationError('The Date of Birth shows that you are not over 21')
    return data


class UpdateAddressForm(forms.ModelForm):

  class Meta:
    model = Address

  def __init__(self, *args, **kwargs):
    super(UpdateAddressForm, self).__init__(*args, **kwargs)


class ForgotPasswordForm(forms.Form):

  email = forms.EmailField()

  def clean_email(self):
    requester_email = self.cleaned_data['email'].strip().lower()
    try:
      u = User.objects.get(email=requester_email)
    except User.DoesNotExist:
      raise forms.ValidationError('User with %s does not exist' % (requester_email))

    return requester_email


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
  exp_month = forms.ChoiceField(required=True, choices=[(x, x) for x in xrange(1, 13)], label="Expiration Date")
  exp_year = forms.ChoiceField(required=True, choices=[(x, x) for x in xrange(date.today().year, date.today().year + 15)])
  verification_code = forms.IntegerField(required = True, label = "CVC Number",
      max_value = 9999, widget = forms.PasswordInput())
  billing_zipcode = us_forms.USZipCodeField()
  #save_card = forms.BooleanField(label="Save this card in My Account", required=False)

  class Meta:
    model = CreditCard

  def __init__(self, *args, **kwargs):
    self.payment_data = kwargs.pop('payment_data', None)
    super(PaymentForm, self).__init__(*args, **kwargs)
    # self.fields['verification_code'].widget = forms.PasswordInput()
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


from django.contrib.auth.models import Group
from emailusernames.forms import NameEmailUserCreationForm, EmailAuthenticationForm
from django.utils.translation import ugettext_lazy as _

ERROR_MESSAGE_INACTIVE = _("Your account has not been verified.  Please verify your account by clicking the link in your \"Welcome to Vinely\" or \"Join Vinely Party!\" e-mail.")

class NameEmailUserMentorCreationForm(NameEmailUserCreationForm):
  mentor = forms.EmailField(required=False, label="Vinely Pro Mentor (Email)")
  zipcode = us_forms.USZipCodeField() #forms.CharField(max_length=20)
  phone_number = us_forms.USPhoneNumberField(required=False)

  def __init__(self, *args, **kwargs):
    super(NameEmailUserMentorCreationForm, self).__init__(*args, **kwargs)
    self.fields['first_name'].required = True
    self.fields['last_name'].required = True
    self.initial = kwargs['initial']

  def clean(self):
    cleaned = super(NameEmailUserMentorCreationForm, self).clean()

    # if signing up for vinely event then allow to add to event without creating new user
    if (self._errors.get('email') == self.error_class(['A user with that email already exists.'])) and self.initial.get('vinely_event'):
        del self._errors['email']

    pro_group = Group.objects.get(name="Vinely Pro")

    mentor_email = self.cleaned_data['mentor'].strip().lower()
    if self.initial['account_type'] == 1 and mentor_email:  # pro -> mentor field
      try:
        # make sure the pro exists
        pro = User.objects.get(email = mentor_email, groups__in = [pro_group])
      except User.DoesNotExist:
        raise forms.ValidationError("The mentor you specified is not a Vinely Pro. Please verify the email address or leave it blank and a mentor will be assigned to you")

    if self.initial['account_type'] == 2 and self.cleaned_data['mentor']:  # host -> pro field
      try:
        # make sure the pro exists
        pro = User.objects.get(email = mentor_email, groups__in = [pro_group])
      except User.DoesNotExist:
        raise forms.ValidationError("The Pro email you specified is not a Vinley Pro's. Please verify the email address or leave it blank and a Pro will be assigned to you")

    if cleaned.get('email'):
      cleaned['email'] = cleaned['email'].strip().lower()
    cleaned['mentor'] = mentor_email
    return cleaned


class HeardAboutForm(forms.Form):
  SOURCES = (
    (0, "A Party"),
    (1, "Print Materials"),
    (2, "Vinely Pro"),
    (3, "Word of mouth"),
    (4, "Other")
  )
  source = forms.ChoiceField(choices=SOURCES)
  description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'class': 'span6'}))

class VinelyEmailAuthenticationForm(EmailAuthenticationForm):

  message_inactive = ERROR_MESSAGE_INACTIVE

  def __init__(self, request=None, *args, **kwargs):
    super(VinelyEmailAuthenticationForm, self).__init__(request, *args, **kwargs)
