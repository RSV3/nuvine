from django import forms
from django.contrib.auth.models import User
from django.contrib.localflavor.us import forms as us_forms
from django.utils.translation import ugettext_lazy as _

from emailusernames.forms import EmailUserChangeForm, UserCreationForm
from emailusernames.utils import user_exists

from accounts.models import Address, UserProfile, CreditCard, SubscriptionInfo
from creditcard.fields import *
from main.models import CustomizeOrder

from main.utils import UTC, add_form_validation
from datetime import datetime, timedelta
import math
from django.forms.extras.widgets import SelectDateWidget


class NameEmailUserCreationForm(UserCreationForm):
    """
    Override the default UserCreationForm to force email-as-username behavior.
    """
    email = forms.EmailField(label=_("Email"), max_length=75)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email",)

    def __init__(self, *args, **kwargs):
        super(NameEmailUserCreationForm, self).__init__(*args, **kwargs)
        del self.fields['username']

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        # if user already exists and is not verified then dont allow signup
        try:
          u = User.objects.get(email=email)
          if u.is_active:
            raise forms.ValidationError(_("A user with that email already exists."))
        except User.DoesNotExist:
          pass
        return email


class UserInfoForm(EmailUserChangeForm):

  class Meta:
    model = User
    exclude = ['last_login', 'groups', 'date_joined', 'is_active', 'is_staff', 'is_superuser']

  def __init__(self, *args, **kwargs):
      super(UserInfoForm, self).__init__(*args, **kwargs)
      self.fields['first_name'].required = True
      self.fields['last_name'].required = True


class ImagePhoneForm(forms.ModelForm):

  class Meta:
    model = UserProfile
    fields = ['image', 'phone']

  def __init__(self, *args, **kwargs):
      super(ImagePhoneForm, self).__init__(*args, **kwargs)
      self.fields['phone'].required = True


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
  # accepted_tos = forms.BooleanField(label="I accept the terms of service")

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


class VerifyEligibilityForm(forms.ModelForm):

  class Meta:
    model = UserProfile
    fields = ['dob', 'user', 'gender', 'dl_number', 'zipcode', 'accepted_tos', 'above_21']
    # exclude = ['wine_personality', 'prequestionnaire', 'billing_address', 'shipping_address', 'phone', 'credits'
    #           'credit_card', 'credit_cards', 'party_addresses', 'shipping_addresses', 'mentor', 'stripe_card', 'stripe_cards']

  def __init__(self, *args, **kwargs):
    super(VerifyEligibilityForm, self).__init__(*args, **kwargs)
    # self.fields['dob'].widget.attrs = {'class': 'datepicker', 'data-date-viewmode': 'years'}
    today = datetime.now().year
    hundred_ago = today - 100
    self.fields['dob'].widget = SelectDateWidget(years=[x for x in range(today - 21, hundred_ago, -1)])
    self.fields['dob'].widget.attrs = {'class': 'select-date'}
    self.fields['user'].widget = forms.HiddenInput()

  def clean(self):
    data = super(VerifyEligibilityForm, self).clean()
    dob = data.get('dob')

    if dob:
      today = datetime.date(datetime.now(tz=UTC()))
      datediff = today - dob
      if (datediff.days < timedelta(math.ceil(365.25 * 21)).days and data['above_21']) or (not dob and data['above_21']):
        # raise forms.ValidationError('The Date of Birth shows that you are not over 21')
        self._errors["dob"] = self.error_class([u"The Date of Birth shows that you are not over 21"])
    return data


class AgeValidityForm(forms.ModelForm):
  class Meta:
    model = UserProfile
    fields = ['dob']

  def __init__(self, *args, **kwargs):
    super(AgeValidityForm, self).__init__(*args, **kwargs)
    # self.fields['dob'].widget.attrs = {
    #     'class': 'datepicker input-block-level',
    #     'data-date-viewmode': 'years',
    #     'data-date-format': 'mm/dd/yyyy',
    #     'placeholder': 'MM/DD/YYYY',
    # }
    today = datetime.now().year
    hundred_ago = today - 100
    self.fields['dob'].widget = SelectDateWidget(years=[x for x in range(today - 21, hundred_ago, -1)])
    self.fields['dob'].widget.attrs = {'class': 'select-date'}
    add_form_validation(self)
    # self.fields['mentor'].widget = forms.HiddenInput()
    # self.fields['gender'].widget = forms.HiddenInput()

  def clean(self):
    data = super(AgeValidityForm, self).clean()
    dob = data.get('dob')

    if dob:
      today = datetime.date(datetime.now(tz=UTC()))
      datediff = today - dob
      if datediff.days < timedelta(math.ceil(365.25 * 21)).days:
        self._errors["dob"] = self.error_class(["You cannot order wine until you verify that you are not under 21"])
    else:
      self._errors["dob"] = self.error_class(["You cannot order wine until you verify that you are not under 21"])
    return data


class UpdateAddressForm(forms.ModelForm):

  same_as_shipping = forms.BooleanField(required=False, label="Same as shipping address")

  class Meta:
    model = Address

  def save(self, commit=True):
    data = self.cleaned_data
    address_values = ['street1', 'street2', 'city', 'state', 'zipcode', 'company_co']
    address_set = set(address_values)
    address_changed = address_set.intersection(self.changed_data)
    if address_changed:
      new_shipping = Address(street1=data['street1'],
                            street2=data['street2'],
                            city=data['city'],
                            state=data['state'],
                            zipcode=data['zipcode'])
      if data['company_co']:
        new_shipping.company_co = data['company_co']
      new_shipping.save()

      self.user_profile.shipping_address = new_shipping
      self.user_profile.shipping_addresses.add(new_shipping)
      self.user_profile.save()
    else:
      new_shipping = self.instance

    return new_shipping


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
  card_number = CreditCardField(required=True, label="Card Number")
  exp_month = forms.ChoiceField(required=True, choices=[(x, x) for x in xrange(1, 13)], label="Expiration Date")
  exp_year = forms.ChoiceField(required=True, choices=[(x, x) for x in xrange(date.today().year, date.today().year + 15)])
  verification_code = forms.IntegerField(required=True, label="CVC Number",
      max_value=9999, widget=forms.PasswordInput())
  billing_zipcode = us_forms.USZipCodeField(label="Billing Zipcode")
  #save_card = forms.BooleanField(label="Save this card in My Account", required=False)

  class Meta:
    model = CreditCard

  def __init__(self, *args, **kwargs):
    self.payment_data = kwargs.pop('payment_data', None)
    super(PaymentForm, self).__init__(*args, **kwargs)
    self.fields['card_number'].widget.attrs['autocomplete'] = 'off'
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
  wine_mix = forms.ChoiceField(choices=CustomizeOrder.MIX_CHOICES)
  sparkling = forms.ChoiceField(choices=CustomizeOrder.SPARKLING_CHOICES)

  class Meta:
    model = SubscriptionInfo
    exclude = ['next_invoice_date']

  def __init__(self, *args, **kwargs):
    super(UpdateSubscriptionForm, self).__init__(*args, **kwargs)
    self.fields['user'].widget = forms.HiddenInput()
    self.fields['quantity'].widget.choices = [('', '---------'), (12, '3 Bottles'), (13, '6 Bottles'), (14, '12 Bottles')]


from emailusernames.forms import EmailAuthenticationForm
from django.utils.translation import ugettext_lazy as _

ERROR_MESSAGE_INACTIVE = _("Your account has not been verified.  Please verify your account by clicking the link in your \"Welcome to Vinely\" or \"Join Vinely Party!\" e-mail.")


class NameEmailUserMentorCreationForm(NameEmailUserCreationForm):
  """
    The form is used for user creation when people sign up for host or pro,
  """

  mentor = forms.EmailField(required=False, label="Your Vinely Pro Email")
  zipcode = us_forms.USZipCodeField()
  phone_number = us_forms.USPhoneNumberField()

  def __init__(self, *args, **kwargs):
    super(NameEmailUserMentorCreationForm, self).__init__(*args, **kwargs)
    self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
    self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
    self.fields['email'].widget.attrs['placeholder'] = 'Email'
    self.fields['zipcode'].widget.attrs['placeholder'] = 'Zip Code'
    self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'
    self.fields['password1'].widget.attrs['placeholder'] = 'Password'
    self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
    self.fields['mentor'].widget.attrs['placeholder'] = 'Your Vinely Pro Email (Optional)'

    self.fields['first_name'].required = True
    self.fields['last_name'].required = True
    self.initial = kwargs.get('initial', {})
    add_form_validation(self)
    self.fields['password2'].widget.attrs['class'] = "validate[required,equals[id_password1]]"
    for field_name in self.fields:
      if 'class' in self.fields[field_name].widget.attrs:
        self.fields[field_name].widget.attrs['class'] += ' input-block-level'
      else:
        self.fields[field_name].widget.attrs['class'] = ' input-block-level'

  def clean(self):
    cleaned = super(NameEmailUserMentorCreationForm, self).clean()

    mentor_email = cleaned.get('mentor')
    if mentor_email:
      mentor_email = mentor_email.strip().lower()

    if self.initial.get('account_type') == 1 and mentor_email:  # pro -> mentor field
      # make sure the pro exists
      if not User.objects.filter(email=mentor_email, userprofile__role=UserProfile.ROLE_CHOICES[1][0]).exists():
        self._errors['mentor'] = "The mentor you specified is not a Vinely Pro. Please verify the email address or leave it blank and a mentor will be assigned to you"

    if self.initial.get('account_type') == 2 and mentor_email or self.initial.get('account_type') == 3 and mentor_email:  # host -> pro field
      # make sure the pro exists
      if not User.objects.filter(email=mentor_email, userprofile__role=UserProfile.ROLE_CHOICES[1][0]).exists():
        self._errors['mentor'] = "The Pro email you specified is not for a Vinley Pro. Please verify the email address or leave it blank and a Pro will be assigned to you"

    if cleaned.get('email'):
      cleaned['email'] = cleaned['email'].strip().lower()
    cleaned['mentor'] = mentor_email
    return cleaned


class MakeHostProForm(NameEmailUserMentorCreationForm):
  '''
  This for is used by users that are already authenticated to provide the extra
  info needed to make them host or pro
  '''
  def __init__(self, *args, **kwargs):
    super(MakeHostProForm, self).__init__(*args, **kwargs)
    self.fields['email'].widget.attrs['readonly'] = True

  def clean_email(self):
    return self.instance.email

  def clean(self):
    cleaned = super(MakeHostProForm, self).clean()

    # if signing up for vinely event then allow to add to event without creating new user
    if (self._errors.get('email') == self.error_class(['A user with that email already exists.'])) and self.initial.get('make_host_or_pro'):
        del self._errors['email']

    if cleaned.get('email'):
      cleaned['email'] = cleaned['email'].strip().lower()
    return cleaned


class NewHostProForm(NameEmailUserMentorCreationForm):
  def __init__(self, *args, **kwargs):
    super(NewHostProForm, self).__init__(*args, **kwargs)


class MakeTasterForm(NameEmailUserMentorCreationForm):
  phone_number = us_forms.USPhoneNumberField(required=False)

  def __init__(self, *args, **kwargs):
    super(MakeTasterForm, self).__init__(*args, **kwargs)
    self.fields['phone_number'].widget.attrs = {'placeholder': 'Phone number (optional)'}
    if self.instance and self.instance.is_active:
      self.fields['email'].widget.attrs['readonly'] = True

  def clean_email(self):
    email = self.cleaned_data['email'].strip().lower()
    if self.instance and self.instance.is_active:
      email = self.instance.email
    return email

  def clean(self):
    cleaned = super(MakeTasterForm, self).clean()

    # if new inactive user, allow to login
    if self.instance and not self.instance.is_active and (self._errors.get('email') == self.error_class(['A user with that email already exists.'])):
        del self._errors['email']

    if cleaned.get('email'):
      cleaned['email'] = cleaned['email'].strip().lower()
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
    self.fields['email'].widget.attrs['placeholder'] = 'Email'
    self.fields['password'].widget.attrs['placeholder'] = 'Password'
    for field_name in self.fields:
      if 'class' in self.fields[field_name].widget.attrs:
        self.fields[field_name].widget.attrs['class'] += ' input-block-level'
      else:
        self.fields[field_name].widget.attrs['class'] = ' input-block-level'


class ProLinkForm(forms.Form):
  email = forms.EmailField(label="Vinely Pro (Email)")

  def clean_email(self):
    cleaned_email = self.cleaned_data['email'].strip().lower()

    if not User.objects.filter(email=cleaned_email, userprofile__role=UserProfile.ROLE_CHOICES[1][0]).exists():
      raise forms.ValidationError('Pro with the email %s does not exist' % (cleaned_email))

    return cleaned_email
