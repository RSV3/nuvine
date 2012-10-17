from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.localflavor.us import forms as us_forms
from django.contrib.localflavor.us import us_states

from emailusernames.utils import create_user, create_superuser
from emailusernames.forms import EmailUserCreationForm

from main.models import Party, PartyInvite, ContactRequest, LineItem, CustomizeOrder, \
                        InvitationSent, Order, Product, ThankYouNote
from accounts.models import Address

import uuid, string


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

  event_day = forms.DateField(label="Taste Party Date")
  event_time = forms.TimeField(input_formats=valid_time_formats, label="Taste Party Time")

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
    self.fields['title'].initial = 'First Taste Party'

  def clean_email(self):
    host_email = self.cleaned_data['email']
    try:
      user = User.objects.get(email=host_email)
        # check if host is not a pro
      pro_group = Group.objects.get(name="Vinely Pro")
      if pro_group in user.groups.all():
        self._errors['email'] = "The host e-mail is associated with a Vinely Pro and cannot host a party."
    except User.DoesNotExist:
      # user with this new e-mail will be created in clean
      pass

    return host_email

  def clean(self):
    cleaned_data = super(PartyCreateForm, self).clean()

    if 'host' not in cleaned_data:
      # create new host or find existing host
      if cleaned_data['email']:
        # create new host based on e-mail
        try:
          user = User.objects.get(email=cleaned_data['email'].lower())
        except User.DoesNotExist:
          user = create_user(email=cleaned_data['email'].lower(), password='welcome')
          user.is_active = False
          user.first_name = cleaned_data['first_name']
          user.last_name = cleaned_data['last_name']
          user.save()

        pro_group = Group.objects.get(name="Vinely Pro")
        ph_group = Group.objects.get(name="Vinely Host")
        if ph_group not in user.groups.all() and pro_group not in user.groups.all():
          # add the user to Vinely Host group if not a Vinely Pro already
          user.groups.clear()
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
      cleaned_data['title'] = "%s's Party" % cleaned_data['host'].first_name
      del self._errors['title']

    if 'event_day' in cleaned_data and 'event_time' in cleaned_data:
      cleaned_data['event_date'] = "%s %s" % (cleaned_data['event_day'], cleaned_data['event_time'])
      del self._errors['event_date']
    else:
      raise forms.ValidationError("Party date and time are required.")

    return cleaned_data

class PartyInviteTasterForm(forms.ModelForm):
  """
    Invite a new taster
  """

  first_name = forms.CharField(max_length=30, required=False)
  last_name = forms.CharField(max_length=30, required=False)
  email = forms.EmailField(required=False)

  class Meta:
    model = PartyInvite
    exclude = ['response']

  def __init__(self, *args, **kwargs):
    super(PartyInviteTasterForm, self).__init__(*args, **kwargs)
    
    initial = kwargs.get('initial')
    att_group = Group.objects.get(name="Vinely Taster")

    if initial.get('host'):
      # only get users linked to this host
      my_guests = PartyInvite.objects.filter(party__host=initial.get('host'))
      users = User.objects.filter(id__in = [x.invitee.id for x in my_guests], groups__in=[att_group]).order_by('first_name')
    elif initial.get('pro'):
      # only get users linked to this host
      my_guests = PartyInvite.objects.filter(party__organizedparty__pro=initial.get('pro'))
      users = User.objects.filter(id__in = [x.invitee.id for x in my_guests], groups__in=[att_group]).order_by('first_name')
    else:
      # everything
      users = User.objects.filter(groups__in=[att_group])
    
    self.fields['invitee'].choices = [('', '---------')]+[(u.id, "%s %s (%s)" % (u.first_name, u.last_name, u.email)) for u in users.only('id','email')]

  def clean(self):
    cleaned_data = super(PartyInviteTasterForm, self).clean()

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
        # add the user to Party Taster group
        att_group = Group.objects.get(name="Vinely Taster")
        user.groups.add(att_group)
        user.save()

      cleaned_data['invitee'] = user
      del self._errors['invitee']

    if 'party' in cleaned_data and 'invitee' in cleaned_data:
      party_invited = PartyInvite.objects.filter(party=cleaned_data['party'], invitee=cleaned_data['invitee'])
      if party_invited.exists():
        raise forms.ValidationError("Invitee already has been invited to the party")

    return cleaned_data

class VinelyProSignupForm(EmailUserCreationForm):
  """
    Create a new Vinely Pro candidate
  """

  phone = forms.CharField(max_length=16)

  street1 = forms.CharField(label="Address 1", max_length=128, required=False)
  street2 = forms.CharField(label="Address 2", max_length=128, required=False)
  city = forms.CharField(label="City", max_length=64, required=False)
  state = forms.CharField(max_length=10, required=False)
  zipcode = us_forms.USZipCodeField(required=False)

  def __init__(self, *args, **kwargs):
    super(VinelyProSignupForm, self).__init__(*args, **kwargs)

  def clean_phone(self):
    data = self.cleaned_data['phone']
    table = string.maketrans("", "")
    stripped_phone = data.translate(table, string.punctuation + string.whitespace)
    if (stripped_phone[0] == 1 and len(stripped_phone) != 11) or len(stripped_phone) != 10:
      raise forms.ValidationError("US phone number is invalid")

    return stripped_phone

  def save(self, commit=True):
    instance = super(VinelyProSignupForm, self).save(commit)

    try:
      address = Address.objects.get(street1=self.cleaned_data['street1'], street2=self.cleaned_data['street2'], city=self.cleaned_data['city'], state=self.cleaned_data['state'], zipcode=self.cleaned_data['zipcode'])
    except Address.DoesNotExist:
      address = Address(street1=self.cleaned_data['street1'],
                        street2=self.cleaned_data['street2'],
                        city=self.cleaned_data['city'],
                        state=self.cleaned_data['state'],
                        zipcode=self.cleaned_data['zipcode'])
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
    if cleaned_data['level'] == "basic":
      if quantity == 1:
        price_category = 5
      elif quantity == 2:
        price_category = 6
    elif cleaned_data['level'] == "superior":
      if quantity == 1:
        price_category = 7
      elif quantity == 2:
        price_category = 8
    elif cleaned_data['level'] == "divine":
      if quantity == 1:
        price_category = 9
      elif quantity == 2:
        price_category = 10

    cleaned_data['price_category'] = price_category
    del self._errors['price_category']

    return cleaned_data

class AddTastingKitToCartForm(forms.ModelForm):
  product = forms.ModelChoiceField(queryset=Product.objects.filter(category=Product.PRODUCT_TYPE[0][0]))
  #quantity = forms.ChoiceField(choices=((0, 1), (1, 2)))

  def __init__(self, *args, **kwargs):
    super(AddTastingKitToCartForm, self).__init__(*args, **kwargs)
    self.fields['total_price'].widget = forms.HiddenInput()
    self.fields['frequency'].widget = forms.HiddenInput()
    self.fields['price_category'].widget = forms.HiddenInput()
    #self.fields['quantity'].widget = forms.HiddenInput()
    self.fields['quantity'].widget = forms.Select()
    self.fields['quantity'].widget.choices = [(1, 1), (2, 2)]

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

  first_name = forms.CharField(max_length=30)
  last_name = forms.CharField(max_length=30)

  address1 = forms.CharField(label="Address 1", max_length=128)
  address2 = forms.CharField(label="Address 2", max_length=128, required=False)
  company_co = forms.CharField(label="Company or C/O", max_length=64, required=False)
  city = forms.CharField(label="City", max_length=64)
  state = us_forms.USStateField()  #choices=us_states.STATE_CHOICES)
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

class CustomizeInvitationForm(forms.ModelForm):

  preview = forms.BooleanField(required=False)
  send = forms.BooleanField(required=False)

  class Meta:
    model = InvitationSent

  def __init__(self, *args, **kwargs):
    super(CustomizeInvitationForm, self).__init__(*args, **kwargs)
    self.fields['custom_subject'].widget.attrs['class'] = 'span4'
    self.fields['party'].widget = forms.HiddenInput()
    self.fields['custom_message'].widget = forms.Textarea(attrs={'rows': 5})

class CustomizeThankYouNoteForm(forms.ModelForm):

  preview = forms.BooleanField(required=False)
  send = forms.BooleanField(required=False)

  class Meta:
    model = ThankYouNote

  def __init__(self, *args, **kwargs):
    super(CustomizeThankYouNoteForm, self).__init__(*args, **kwargs)
    self.fields['custom_subject'].widget.attrs['class'] = 'span5'
    self.fields['party'].widget = forms.HiddenInput()
    self.fields['custom_message'].widget = forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your custom thank you note.'})

class OrderFulfillForm(forms.ModelForm):

  class Meta:
    model = Order
    exclude = ['ordered_by', 'receiver', 'cart', 'shipping_address', 'credit_card', 'order_date',
                'ship_date', 'last_updated']

  def __init__(self, *args, **kwargs):
    super(OrderFulfillForm, self).__init__(*args, **kwargs)
    self.fields['order_id'].widget = forms.HiddenInput()

