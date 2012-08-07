from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.localflavor.us import forms as us_forms
from django.contrib.localflavor.us import us_states

from emailusernames.utils import create_user, create_superuser
from emailusernames.forms import EmailUserCreationForm

from main.models import Party, PartyInvite, ContactRequest, LineItem, CustomizeOrder, \
                        InvitationSent, Order
from accounts.models import Address, CreditCard
from creditcard.fields import *

import uuid


valid_time_formats = ['%H:%M', '%I:%M %p', '%I:%M%p']

class ContactRequestForm(forms.ModelForm):

  zipcode = us_forms.USZipCodeField()
  phone = us_forms.USPhoneNumberField()

  def __init__(self, *args, **kwargs):
    super(ContactRequestForm, self).__init__(*args, **kwargs)
    self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
    self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'

  class Meta:
    model = ContactRequest

class PartyCreateForm(forms.ModelForm):

  first_name = forms.CharField(max_length=30, required=False)
  last_name = forms.CharField(max_length=30, required=False)
  email = forms.EmailField(required=False)

  street1 = forms.CharField(label="Street 1", max_length=128, required=False)
  street2 = forms.CharField(label="Street 2", max_length=128, required=False)
  city = forms.CharField(label="City", max_length=64, required=False)
  state = us_forms.USStateField(required=False)
  zipcode = us_forms.USZipCodeField(required=False)

  event_day = forms.DateField(label="Event date")
  event_time = forms.TimeField(input_formats=valid_time_formats)

  # replace form field for Party.phone
  phone = us_forms.USPhoneNumberField()

  class Meta:
    model = Party

  def __init__(self, *args, **kwargs):
    super(PartyCreateForm, self).__init__(*args, **kwargs)
    self.fields['event_day'].widget.attrs['class'] = 'datepicker'
    self.fields['event_time'].widget.attrs['class'] = 'timepicker'
    self.fields['event_date'].widget = forms.HiddenInput()
    self.fields['description'].required = False

  def clean(self):
    cleaned_data = super(PartyCreateForm, self).clean()

    if 'host' not in cleaned_data: 
      # create new host or find existing host 
      try:
        user = User.objects.get(email=cleaned_data['email'].lower())
      except User.DoesNotExist:
        user = create_user(email=cleaned_data['email'].lower(), password='welcome')
        user.is_active = False
        user.first_name = cleaned_data['first_name']
        user.last_name = cleaned_data['last_name']
        user.save()

      ps_group = Group.objects.get(name="Party Specialist")
      if ps_group not in user.groups.all():
        # add the user to Party Host group if not a party specialist already
        ph_group = Group.objects.get(name="Party Host")
        user.groups.add(ph_group)
        user.save()

      cleaned_data['host'] = user 
      del self._errors['host']

    if 'address' not in cleaned_data:
      # create new address
      try:
        address = Address.objects.get(street1=cleaned_data['street1'], street2=cleaned_data['street2'], city=cleaned_data['city'], state=cleaned_data['state'], zipcode=cleaned_data['zipcode'])
      except Address.DoesNotExist:
        # TODO: need to check whether these fields are all filled out
        address = Address(street1=cleaned_data['street1'],
                          street2=cleaned_data['street2'],
                          city=cleaned_data['city'],
                          state=cleaned_data['state'],
                          zipcode=cleaned_data['zipcode'])
        address.save()

      cleaned_data['address'] = address
      del self._errors['address']

    if 'title' not in cleaned_data:
      cleaned_data['title'] = "%s's Party"%cleaned_data['host'].first_name
      del self._errors['title']

    if 'event_day' in cleaned_data and 'event_time' in cleaned_data:
      cleaned_data['event_date'] = "%s %s"%(cleaned_data['event_day'], cleaned_data['event_time'])
      del self._errors['event_date']
    else:
      raise forms.ValidationError("Party date and time are required.")

    return cleaned_data 

class PartyInviteAttendeeForm(forms.ModelForm):
  """
    Invite a new attendee
  """

  first_name = forms.CharField(max_length=30, required=False)
  last_name = forms.CharField(max_length=30, required=False)
  email = forms.EmailField(required=False)

  class Meta:
    model = PartyInvite
    exclude = ['response']

  def __init__(self, *args, **kwargs):
    super(PartyInviteAttendeeForm, self).__init__(*args, **kwargs)
    att_group = Group.objects.get(name="Attendee")
    self.fields['invitee'].choices = [('', '---------')]+[(u.id, u.email) for u in User.objects.filter(groups__in=[att_group]).only('id','email')]

  def clean(self):
    cleaned_data = super(PartyInviteAttendeeForm, self).clean()

    if 'invitee' not in cleaned_data: 
      # create new host and return host ID
      try:
        user = User.objects.get(email=cleaned_data['email'].lower())
      except User.DoesNotExist:
        user = create_user(email=cleaned_data['email'].lower(), password='welcome')
        user.first_name = cleaned_data['first_name']
        user.last_name = cleaned_data['last_name']
        user.is_active = False
        user.save()

      if user.groups.all().count() == 0:
        # add the user to Party Attendee group
        att_group = Group.objects.get(name="Attendee")
        user.groups.add(att_group)
        user.save()

      cleaned_data['invitee'] = user 
      del self._errors['invitee']

    if 'party' in cleaned_data and 'invitee' in cleaned_data:
      party_invited = PartyInvite.objects.filter(party=cleaned_data['party'], invitee=cleaned_data['invitee'])
      if party_invited.exists():
        raise forms.ValidationError("Invitee already has been invited to the party")

    return cleaned_data

class PartySpecialistSignupForm(EmailUserCreationForm):
  """
    Create a new party specialist candidate
  """

  phone = forms.CharField(max_length=16)

  street1 = forms.CharField(label="Address 1", max_length=128, required=False)
  street2 = forms.CharField(label="Address 2", max_length=128, required=False)
  city = forms.CharField(label="City", max_length=64, required=False)
  state = forms.CharField(max_length=10, required=False)
  zipcode = us_forms.USZipCodeField(required=False)

  def __init__(self, *args, **kwargs):
    super(PartySpecialistSignupForm, self).__init__(*args, **kwargs)

  def clean_phone(self):
    data = self.cleaned_data['phone']
    table = string.maketrans("", "")
    stripped_phone = data.translate(table, string.punctuation+string.whitespace)
    if (stripped_phone[0] == 1 and len(stripped_phone) != 11) or len(stripped_phone) != 10:
      raise forms.ValidationError("US phone number is invalid")

    return stripped_phone

  def save(self, commit=True):
    instance = super(PartySpecialistSignUpForm, self).save(commit)

    try:
      address = Address.objects.get(street1=cleaned_data['street1'], street2=cleaned_data['street2'], city=cleaned_data['city'], state=cleaned_data['state'], zipcode=cleaned_data['zipcode'])
    except Address.DoesNotExist:
      address = Address(street1=cleaned_data['street1'],
                        street2=cleaned_data['street2'],
                        city=cleaned_data['city'],
                        state=cleaned_data['state'],
                        zipcode=cleaned_data['zipcode'])
      address.save()

    return instance


class AddWineToCartForm(forms.ModelForm):
  level = forms.CharField(widget=forms.HiddenInput)

  def __init__(self, *args, **kwargs):
    super(AddWineToCartForm, self).__init__(*args, **kwargs)
    self.fields['quantity'].widget = forms.Select() 
    self.fields['quantity'].widget.choices = [(1, 'Full Case'), (2, 'Half Case')] 
    self.fields['product'].widget = forms.HiddenInput()
    self.fields['total_price'].widget = forms.HiddenInput()

  class Meta:
    model = LineItem 
    exclude = ['sku']

  def clean(self):
    cleaned_data = super(AddWineToCartForm, self).clean()

    quantity = int(cleaned_data['quantity'])
    if cleaned_data['level'] == "good":
      if quantity == 1:
        price_category = 5
      elif quantity == 2:
        price_category = 6
    elif cleaned_data['level'] == "better":
      if quantity == 1:
        price_category = 7
      elif quantity == 2:
        price_category = 8
    elif cleaned_data['level'] == "best":
      if quantity == 1:
        price_category = 9 
      elif quantity == 2:
        price_category = 10 
      
    cleaned_data['price_category'] = price_category
    del self._errors['price_category']

    return cleaned_data

class AddTastingKitToCartForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    super(AddTastingKitToCartForm, self).__init__(*args, **kwargs)
    self.fields['product'].widget = forms.HiddenInput()
    self.fields['total_price'].widget = forms.HiddenInput()
    self.fields['frequency'].widget = forms.HiddenInput()
    self.fields['price_category'].widget = forms.HiddenInput()
    self.fields['quantity'].widget = forms.Select() 
    self.fields['quantity'].widget.choices = [(1, 1), (2, 2), (3, 3)] 

  class Meta:
    model = LineItem 

  def clean(self):
    cleaned_data = super(AddTastingKitToCartForm, self).clean()
    cleaned_data['price_category'] = 11 
    cleaned_data['frequency'] = 0

    return cleaned_data

class CustomizeOrderForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    super(CustomizeOrderForm, self).__init__(*args, **kwargs)
    self.fields['wine_mix'].widget = forms.RadioSelect(choices=CustomizeOrder.MIX_CHOICES)
    self.fields['sparkling'].widget = forms.RadioSelect(choices=CustomizeOrder.SPARKLING_CHOICES)

  class Meta:
    model = CustomizeOrder
    exclude = ['user', 'timestamp']

class ShippingForm(forms.ModelForm):

  first_name = forms.CharField(max_length=30, required=False)
  last_name = forms.CharField(max_length=30, required=False)

  address1 = forms.CharField(label="Address 1", max_length=128)
  address2 = forms.CharField(label="Address 2", max_length=128, required=False)
  company_co = forms.CharField(label="Company or C/O", max_length=64, required=False)
  city = forms.CharField(label="City", max_length=64, required=False)
  state = us_forms.USStateField() #choices=us_states.STATE_CHOICES)
  zipcode = us_forms.USZipCodeField()
  phone = us_forms.USPhoneNumberField()
  email = forms.EmailField(help_text="A new account will be created using this e-mail address if not an active account")

  news_optin = forms.BooleanField(label="Yes, I'd like to be notified of news, offers and events at Vinely via this email address.", \
                                initial=True, required=False)

  class Meta:
    model = User
    exclude = ['username', 'password', 'last_login', 'date_joined']

  def save(self, commit=True):
    data = self.cleaned_data
    try:
      # existing user
      user = User.objects.get(email=data['email'].lower())
      if not user.first_name: 
        user.first_name = data['first_name']
      if not user.last_name:
        user.last_name = data['last_name']
      user.save()
      # save address
    except User.DoesNotExist:
      # create user if it doesn't exist
      user = create_user(email=data['email'].lower(), password='welcome')
      user.is_active = False 
      user.first_name = data['first_name']
      user.last_name = data['last_name']
      user.save()

    new_shipping = Address( street1 = data['address1'],
                          street2 = data['address2'],
                          city = data['city'],
                          state = data['state'],
                          zipcode = data['zipcode'])
    if data['company_co']:
      new_shipping.company_co = data['company_co']

    new_shipping.save()

    profile = user.get_profile()
    profile.shipping_address = new_shipping
    profile.shipping_addresses.add(new_shipping)
    profile.news_optin = data['news_optin']
    if data['phone']:
      profile.phone = data['phone']
    profile.save()

    return user

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
 
  def clean(self):
    cleaned_data = super(PaymentForm, self).clean()

    exp_month = cleaned_data.get('exp_month')
    exp_year = cleaned_data.get('exp_year')

    if exp_year in forms.fields.EMPTY_VALUES:
      #raise forms.ValidationError("You must select a valid Expiration year.")
      self._errors["exp_year"] = self.error_class(["You must select a valid Expiration year."])
      del cleaned_data["exp_year"]
    if exp_month in forms.fields.EMPTY_VALUES:
      #raise forms.ValidationError("You must select a valid Expiration month.")
      self._errors["exp_month"] = self.error_class(["You must select a valid Expiration month."])
      del cleaned_data["exp_month"]
    year = int(exp_year)
    month = int(exp_month)
    # find last day of the month
    day = monthrange(year, month)[1]
    expire = date(year, month, day)
 
    if date.today() > expire:
      #raise forms.ValidationError("The expiration date you entered is in the past.")
      self._errors["exp_year"] = self.error_class(["The expiration date you entered is in the past."])
 
    return cleaned_data

  def save(self, commit=True, force_insert=False, force_update=False, *args, **kwargs):
    m = super(PaymentForm, self).save(commit=False, *args, **kwargs)

    # encrypt card number
    m.encrypt_card_num(self.cleaned_data['card_number'])

    if commit:
      m.save()
    return m
    
class CustomizeInvitationForm(forms.ModelForm):

  class Meta:
    model = InvitationSent

  def __init__(self, *args, **kwargs):
    super(CustomizeInvitationForm, self).__init__(*args, **kwargs)
    self.fields['custom_subject'].widget.attrs['class'] = 'span4'
    self.fields['party'].widget = forms.HiddenInput()
    self.fields['custom_message'].widget = forms.Textarea(attrs={'rows':5})

class OrderFulfillForm(forms.ModelForm):

  class Meta:
    model = Order
    exclude = ['ordered_by', 'receiver', 'cart', 'shipping_address', 'credit_card', 'order_date',
                'ship_date', 'last_updated']

  def __init__(self, *args, **kwargs):
    super(OrderFulfillForm, self).__init__(*args, **kwargs)
    self.fields['order_id'].widget = forms.HiddenInput()
    