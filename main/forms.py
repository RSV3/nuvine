from django import forms
from django.contrib.auth.models import User, Group
from emailusernames.utils import create_user, create_superuser
from main.models import Party, ContactRequest
from accounts.models import Address

class ContactRequestForm(forms.ModelForm):

  class Meta:
    model = ContactRequest

class PartyCreateForm(forms.ModelForm):

  first_name = forms.CharField(max_length=30)
  last_name = forms.CharField(max_length=30)
  email = forms.EmailField()

  street1 = forms.CharField(label="Street 1", max_length=128)
  street2 = forms.CharField(label="Street 2", max_length=128, required=False)
  city = forms.CharField(label="City", max_length=64)
  state = forms.CharField(max_length=10)
  zipcode = forms.CharField(max_length=20)

  class Meta:
    model = Party

  def __init__(self, *args, **kwargs):
    super(PartyCreateForm, self).__init__(*args, **kwargs)
    self.fields['event_date'].widget.attrs['class'] = 'datepicker'

    ph_group = Group.objects.get(name="Party Host")
    self.fields['host'].queryset = User.objects.filter(groups__in=[ph_group])

  def clean(self):
    cleaned_data = super(PartyCreateForm, self).clean()

    if 'host' not in cleaned_data: 
      # create new host and return host ID
      try:
        user = User.objects.get(email=cleaned_data['email'])
      except User.DoesNotExist:
        user = create_user(email=cleaned_data['email'], password='')

      # add the user to Party Host group
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

    return cleaned_data 

  def save(self, force_insert=False, force_update=False, commit=True):
    m = super(PartyCreateForm, self).save(commit=False)
    data = self.cleaned_data

    """
    if not data['host']:
      try:
        user = User.objects.get(email=data['email'])
      except User.DoesNotExist:
        user = create_user(email=data['email'], password='')

      m.host = user

    if not data['address']:
      try:
        address = Address.objects.get(street1=data['street1'], street2=data['street2'], city=data['city'], state=data['state'], zipcode=data['zipcode'])
      except Address.DoesNotExist:
        address = Address(street1=data['street1'],
                          street2=data['street2'],
                          city=data['city'],
                          state=data['state'],
                          zipcdoe=data['zipcode'])
        address.save()
      
      m.address = address
    """

    if commit:
      m.save()
    return m
