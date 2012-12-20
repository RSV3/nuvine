from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.localflavor.us import forms as us_forms
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from datetime import timedelta

import django_tables2 as tables
from django_tables2 import Attrs

from emailusernames.utils import create_user
from emailusernames.forms import EmailUserCreationForm, NameEmailUserCreationForm

from main.models import Party, PartyInvite, ContactRequest, LineItem, CustomizeOrder, \
                        InvitationSent, Order, Product, ThankYouNote, MyHost
from accounts.models import Address

import string
from lepl.apps.rfc3696 import Email


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

  first_name = forms.CharField(max_length=30)
  last_name = forms.CharField(max_length=30)
  email = forms.EmailField()

  street1 = forms.CharField(label="Street 1", max_length=128, required=False)
  street2 = forms.CharField(label="Street 2", max_length=128, required=False)
  city = forms.CharField(label="City", max_length=64, required=False)
  state = us_forms.USStateField(required=False)
  zipcode = us_forms.USZipCodeField(required=False)

  event_day = forms.DateField(label="Party Date")
  event_time = forms.TimeField(input_formats=valid_time_formats, label="Party Time")

  # replace form field for Party.phone
  phone = us_forms.USPhoneNumberField(required=False)

  class Meta:
    model = Party

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(PartyCreateForm, self).__init__(*args, **kwargs)
    self.fields['event_day'].widget.attrs['class'] = 'datepicker'
    self.fields['event_time'].widget.attrs['class'] = 'timepicker'
    self.fields['event_date'].widget = forms.HiddenInput()
    # self.fields['email'].widget.attrs['readonly'] = True
    self.fields['description'].required = False
    self.fields['title'].initial = 'First Taste Party'
    initial = kwargs.get('initial')

    # if party being organized by host then load previous addresses by host
    if user.userprofile.is_host():
      parties = Party.objects.filter(host=initial['host'])
    else:
      # else if by pro then load prev organized party addresses
      parties = Party.objects.filter(organizedparty__pro=initial.get('pro'))
      my_hosts = MyHost.objects.filter(pro=initial.get('pro'))
      users = User.objects.filter(id__in=[x.host.id for x in my_hosts]).order_by('first_name')
      self.fields['host'].choices = [(u.id, "%s %s (%s)" % (u.first_name, u.last_name, u.email)) for u in users.only('id', 'email')]

    addresses = Address.objects.filter(id__in=[p.address.id for p in parties]).order_by('street1')
    # only show addresses that pro/host has dealt with before
    self.fields['address'].queryset = addresses

  def clean_email(self):
    #1. if current user is host dont allow to set new host via
    if self.initial.get('host'):
      host_email = self.initial['host'].email
    else:
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
    if self._errors.get('host'):
      self._errors['host'] = 'Pick a Host from the list or Enter the Host details below'

    if 'host' in cleaned_data:
      del self._errors['first_name']
      del self._errors['last_name']
      del self._errors['email']
    else:
      # create new host or find existing host
      if cleaned_data.get('email'):
        # create new host based on e-mail
        try:
          user = User.objects.get(email=cleaned_data['email'].lower())
          if not user.first_name:
            user.first_name = cleaned_data['first_name']
            user.last_name = cleaned_data['last_name']
            user.save()
        except User.DoesNotExist:
          user = create_user(email=cleaned_data['email'].lower(), password='welcome')
          user.is_active = False
          user.first_name = cleaned_data['first_name']
          user.last_name = cleaned_data['last_name']
          user.save()

        if 'phone' in cleaned_data:
          prof = user.get_profile()
          prof.phone = cleaned_data['phone']
          prof.save()

        pro_group = Group.objects.get(name="Vinely Pro")
        ph_group = Group.objects.get(name="Vinely Host")
        if ph_group not in user.groups.all() and pro_group not in user.groups.all():
          # add the user to Vinely Host group if not a Vinely Pro already
          user.groups.clear()
          user.groups.add(ph_group)
          user.save()

        cleaned_data['host'] = user
        del self._errors['host']

    if len(cleaned_data['street1']) > 0:
      # create new address
      addresses = Address.objects.filter(street1=cleaned_data['street1'], street2=cleaned_data['street2'], city=cleaned_data['city'], state=cleaned_data['state'], zipcode=cleaned_data['zipcode'])
      if addresses.exists():
        address = addresses[0]
      else:
        # TODO: need to check whether these fields are all filled out
        address = Address(street1=cleaned_data['street1'],
                          street2=cleaned_data['street2'],
                          city=cleaned_data['city'],
                          state=cleaned_data['state'],
                          zipcode=cleaned_data['zipcode'])
        address.save()

      cleaned_data['address'] = address
      if 'address' in self._errors:
        # if no address selected, but street info manually filled out, remove error
        del self._errors['address']

    if 'title' not in cleaned_data:
      cleaned_data['title'] = "%s's Party" % cleaned_data['host'].first_name
      del self._errors['title']

    if 'event_day' in cleaned_data and 'event_time' in cleaned_data:
      full_date = "%s %s" % (cleaned_data['event_day'], cleaned_data['event_time'])
      full_date = timezone.datetime.strptime(full_date, '%Y-%m-%d %H:%M:%S')
      cleaned_data['event_date'] = timezone.make_aware(full_date, timezone.get_current_timezone())
      del self._errors['event_date']

      if (cleaned_data['event_date'] - timezone.now()) < timedelta(days=10):
        raise forms.ValidationError("Your party needs to be more than 10 days from today to ensure that the tasting kit is received in time for the party.")
    else:
      raise forms.ValidationError("Party date and time are required.")

    return cleaned_data


class PartyTasterOptionsForm(forms.Form):
  TASTER_OPTIONS = (
    (0, "see the guest list?"),
    (1, "be able to invite friends?"),
  )

  taster_actions = forms.MultipleChoiceField(choices=TASTER_OPTIONS, widget=forms.CheckboxSelectMultiple, label="Do you want tasters to", required=False)


class PartyInviteTasterForm(forms.ModelForm):
  """
    Invite a new taster
  """

  first_name = forms.CharField(max_length=30)
  last_name = forms.CharField(max_length=30)
  email = forms.EmailField()
  phone = us_forms.USPhoneNumberField(required=False)

  class Meta:
    model = PartyInvite
    # exclude = ['response']

  def __init__(self, *args, **kwargs):
    super(PartyInviteTasterForm, self).__init__(*args, **kwargs)
    initial = kwargs.get('initial')

    self.fields['first_name'].widget.attrs = {"placeholder": "First Name"}
    self.fields['last_name'].widget.attrs = {"placeholder": "Last Name"}
    self.fields['email'].widget.attrs = {"placeholder": "Email"}
    self.fields['phone'].widget.attrs = {"placeholder": "Phone"}
    self.fields['party'].widget = forms.HiddenInput()
    if not initial.get('change_rsvp') == 't':
      self.fields['response'].widget = forms.HiddenInput()

    tas_group = Group.objects.get(name="Vinely Taster")

    if initial.get('host'):
      # only get users linked to this host
      my_guests = PartyInvite.objects.filter(party__host=initial.get('host'))
      users = User.objects.filter(id__in=[x.invitee.id for x in my_guests], groups__in=[tas_group]).order_by('first_name')
    elif initial.get('pro'):
      # only get users linked to this host
      my_guests = PartyInvite.objects.filter(party__organizedparty__pro=initial.get('pro'))
      users = User.objects.filter(id__in=[x.invitee.id for x in my_guests], groups__in=[tas_group]).order_by('first_name')
    else:
      # everything
      users = User.objects.none()

    self.fields['invitee'].choices = [('', '---------')] + [(u.id, "%s %s (%s)" % (u.first_name, u.last_name, u.email)) for u in users.only('id', 'email')]

  def clean(self):

    cleaned_data = super(PartyInviteTasterForm, self).clean()
    email_validator = Email()

    if 'invitee' in cleaned_data:
      if self._errors.get('first_name'):
        del self._errors['first_name']
      if self._errors.get('last_name'):
        del self._errors['last_name']
      if self._errors.get('email'):
        del self._errors['email']
    else:
      # create new host and return host ID
      if email_validator(cleaned_data.get('email')):

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
      else:
        from django.forms.util import ErrorList
        msg = 'Enter valid e-mail for the invitee.'
        self._errors['email'] = ErrorList([msg])
        if self.cleaned_data.get('email'):
          del self.cleaned_data['email']
      # delete error if we think user manually being filled out
      del self._errors['invitee']

    # if user did not manually enter or pick from list of attendees
    if self._errors.get('invitee'):
      raise forms.ValidationError('Pick a guest from the list or Enter the Attendee details to add')

    if 'party' in cleaned_data and 'invitee' in cleaned_data:
      party_invited = PartyInvite.objects.filter(party=cleaned_data['party'], invitee=cleaned_data['invitee'])
      if party_invited.exists():
        raise forms.ValidationError("Invitee (%s) has already been invited to the party" % cleaned_data['invitee'].email)

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
  state = us_forms.USStateField()  # choices=us_states.STATE_CHOICES)
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

    new_shipping = Address(street1=data['address1'],
                          street2=data['address2'],
                          city=data['city'],
                          state=data['state'],
                          zipcode=data['zipcode'])
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

  AUTO_INVITE_OPTIONS = (
    (0, 'send out the party invite automatically as soon as your Pro confirms the time and date?'),
    (1, 'allow you to confirm your invite email again before it is sent out?')
  )
  AUTO_THANK_OPTIONS = (
    (0, 'send out a Thank You email on your behalf automatically after the party? (Preview Email)'),
    (1, 'let me send my own Thank You email after the party')
  )
  GUEST_INVITE_OPTIONS = (
    (1, 'allow guests to invite friends?'),
  )
  preview = forms.BooleanField(required=False)
  send = forms.BooleanField(required=False)
  auto_invite = forms.ChoiceField(choices=AUTO_INVITE_OPTIONS, widget=forms.RadioSelect, required=False)
  auto_thank_you = forms.ChoiceField(choices=AUTO_THANK_OPTIONS, widget=forms.RadioSelect, required=False)
  guests_can_invite = forms.MultipleChoiceField(choices=GUEST_INVITE_OPTIONS, widget=forms.CheckboxSelectMultiple, required=False)

  class Meta:
    model = InvitationSent

  def __init__(self, *args, **kwargs):
    super(CustomizeInvitationForm, self).__init__(*args, **kwargs)
    initial = kwargs.get('initial', {})
    if initial.get('subject'):
      self.fields['custom_subject'].widget = forms.HiddenInput()
    else:
      self.fields['custom_subject'].widget.attrs['class'] = 'span4'
    self.fields['party'].widget = forms.HiddenInput()
    self.fields['custom_message'].widget = forms.Textarea(attrs={'rows': 10})

  def clean_custom_message(self):
    cleaned = self.cleaned_data['custom_message']
    return cleaned.replace('\r', '')


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


class EventSignupForm(NameEmailUserCreationForm):
  '''
    This form is used when inviting people to public Vinely events.
    As a result the clean method has cases to handle creation of new users and users that already exist.
  '''
  zipcode = us_forms.USZipCodeField()

  def clean(self):
    cleaned = super(EventSignupForm, self).clean()

    # if signing up for vinely event then allow to add to event without creating new user
    if (self._errors.get('email') == self.error_class(['A user with that email already exists.'])) and self.initial.get('vinely_event'):
        del self._errors['email']

    if cleaned.get('email'):
      cleaned['email'] = cleaned['email'].strip().lower()
    return cleaned


class ChangeTasterRSVPForm(forms.Form):
  RSVP_CHOICES = (
    (0, '------'),
    (1, 'No'),
    (2, 'Maybe'),
    (3, 'Yes'),
  )
  party = forms.IntegerField(widget=forms.HiddenInput())
  rsvp = forms.ChoiceField(choices=RSVP_CHOICES)


table_attrs = Attrs({'class': 'table table-striped'})

##############################################################################
#
# Django tables
#
##############################################################################


class AttendeesTable(tables.Table):
  guests = tables.CheckBoxColumn(Attrs({'name': 'guests', 'td__input': {'class': 'guest'}, 'th__input': {'class': 'all-guests'}}), accessor='invitee.id')
  invitee = tables.Column(verbose_name='Name', order_by=('invitee.first_name', 'invitee.last_name'))
  email = tables.TemplateColumn('<a href="mailto:{{ record.invitee.email }}">{{ record.invitee.email }}</a>', orderable=False)
  phone = tables.TemplateColumn('{% if record.invitee.userprofile.phone %} {{ record.invitee.userprofile.phone }} {% else %} - {% endif %}', orderable=False)
  response = tables.Column(verbose_name='RSVP')
  invited = tables.TemplateColumn('{% if record.invited %}<i class="icon-ok"></i>{% endif %}', accessor='invited_timestamp', verbose_name='Invited')
  wine_personality = tables.Column(accessor='invitee.userprofile.wine_personality', verbose_name='Wine Personality', order_by=('invitee.userprofile.wine_personality.name',))
  edit = tables.TemplateColumn('<a href="javascript:;" class="edit-taster" data-invite="{{ record.id }}">edit</a>', verbose_name=' ')
  shop = tables.TemplateColumn('<a href="{% url start_order record.invitee.id record.party.id %}" class="btn btn-primary">Shop</a>', verbose_name=' ')
  confirmed = tables.TemplateColumn('<a href="{% url party_remove_taster record.id %}" class="remove-taster" data-invite="{{ record.id }}">X</a>', verbose_name=' ')

  class Meta:
    model = PartyInvite
    attrs = table_attrs
    sequence = ['guests', 'invitee', 'email', 'phone', '...']
    exclude = ['id', 'party', 'invited_by', 'rsvp_code', 'response_timestamp', 'invited_timestamp']
    order_by = ['invitee']

  def __init__(self, *args, **kwargs):
    data = kwargs.pop('data', {})
    user = kwargs.pop('user')
    super(AttendeesTable, self).__init__(*args, **kwargs)

    exclude = list(self.exclude)
    if not (user.userprofile.is_host() or user.userprofile.events_user()):
      exclude.append('guests')
    if not data['can_add_taster']:
      exclude.append('invited')
    if not user.userprofile.is_pro():
      exclude.append('wine_personality')
    if not (user.userprofile.is_host() and data['can_add_taster'] or user.userprofile.is_pro() and data['can_add_taster']):
      exclude.append('edit')
    if data['party'].confirmed:
      exclude.append('confirmed')
    if not (user.userprofile.is_pro() and data['can_shop_for_taster']):
      exclude.append('shop')

    self.exclude = exclude

  def render_invitee(self, record, column):
    if record.invitee.first_name:
      return "%s %s" % (record.invitee.first_name, record.invitee.last_name)
    else:
      return "Anonymous"

  def render_shop(self, record, column):
      if record.invitee.userprofile.has_personality():
        return mark_safe('<a href="%s" class="btn btn-primary">Shop</a>' % reverse('start_order', args=[record.invitee.id, record.party.id]))
      else:
        return ''

  def render_wine_personality(self, record, column):
    if record.invitee.userprofile.has_personality():
      return mark_safe('<a href="%s">%s</a>' % (reverse('personality_rating_info', args=[record.invitee.email, record.party.id]), record.invitee.userprofile.wine_personality))
    else:
      return mark_safe('<a href="%s">Enter ratings</a>' % (reverse('record_all_wine_ratings', args=[record.invitee.email, record.party.id])))
