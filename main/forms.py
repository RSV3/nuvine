from django import forms
from django.contrib.auth.models import User, Group
from emailusernames.utils import create_user, create_superuser
from main.models import Party, PartyInvite, ContactRequest
from accounts.models import Address

from emailusernames.forms import EmailUserCreationForm

class ContactRequestForm(forms.ModelForm):

  class Meta:
    model = ContactRequest

valid_time_formats = ['%H:%M', '%I:%M %p', '%I:%M%p']

class PartyCreateForm(forms.ModelForm):

  first_name = forms.CharField(max_length=30, required=False)
  last_name = forms.CharField(max_length=30, required=False)
  email = forms.EmailField(required=False)

  street1 = forms.CharField(label="Street 1", max_length=128, required=False)
  street2 = forms.CharField(label="Street 2", max_length=128, required=False)
  city = forms.CharField(label="City", max_length=64, required=False)
  state = forms.CharField(max_length=10, required=False)
  zipcode = forms.CharField(max_length=20, required=False)

  event_day = forms.DateField(label="Event date")
  event_time = forms.TimeField(input_formats=valid_time_formats)

  class Meta:
    model = Party

  def __init__(self, *args, **kwargs):
    super(PartyCreateForm, self).__init__(*args, **kwargs)
    self.fields['event_day'].widget.attrs['class'] = 'datepicker'
    self.fields['event_time'].widget.attrs['class'] = 'timepicker'
    self.fields['event_date'].widget = forms.HiddenInput()

    ph_group = Group.objects.get(name="Party Host")
    #self.fields['host'].queryset = User.objects.filter(groups__in=[ph_group]).only('id','email')
    self.fields['host'].choices = [(u.id, u.email) for u in User.objects.filter(groups__in=[ph_group]).only('id','email')]

  def clean(self):
    cleaned_data = super(PartyCreateForm, self).clean()

    if 'host' not in cleaned_data: 
      # create new host and return host ID
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
    self.fields['invitee'].queryset = User.objects.filter(groups__in=[att_group])

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

  street1 = forms.CharField(label="Street 1", max_length=128, required=False)
  street2 = forms.CharField(label="Street 2", max_length=128, required=False)
  city = forms.CharField(label="City", max_length=64, required=False)
  state = forms.CharField(max_length=10, required=False)
  zipcode = forms.CharField(max_length=20, required=False)

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
    instance = super(PartySpecialistSignUpForm, self).save()

    try:
      address = Address.objects.get(street1=cleaned_data['street1'], street2=cleaned_data['street2'], city=cleaned_data['city'], state=cleaned_data['state'], zipcode=cleaned_data['zipcode'])
    except Address.DoesNotExist:
      address = Address(street1=cleaned_data['street1'],
                        street2=cleaned_data['street2'],
                        city=cleaned_data['city'],
                        state=cleaned_data['state'],
                        zipcode=cleaned_data['zipcode'])
      address.save()



