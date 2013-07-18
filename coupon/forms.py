from django import forms
from django.utils import timezone

from coupon.models import Coupon
from main.models import Product


class CouponForm(forms.ModelForm):
  applies_to = forms.ModelMultipleChoiceField(queryset=Product.objects.filter(active=True).order_by('id'), widget=forms.CheckboxSelectMultiple)

  class Meta:
    model = Coupon
    exclude = ['times_redeemed', 'created', 'updated']

  def __init__(self, *args, **kwargs):
    super(CouponForm, self).__init__(*args, **kwargs)
    # self.fields['redeem_by'].widget.attrs['class'] = 'datepicker'
    self.fields['redeem_by'].widget.attrs = {
        'class': 'datepicker',
        'data-date-format': 'mm/dd/yyyy',
        'placeholder': 'MM/DD/YYYY',
    }

    if kwargs.get('instance'):
      self.fields['code'].widget.attrs['readonly'] = True

  def clean_max_redemptions(self):
    cleaned_data = self.cleaned_data.get('max_redemptions', 0)
    if cleaned_data < 1:
      raise forms.ValidationError(u'Max redemptions must be 1 or more.')
    return cleaned_data

  def clean_redeem_by(self):
    cleaned_data = self.cleaned_data.get('redeem_by')
    today = timezone.now().date()
    if cleaned_data <= today:
      raise forms.ValidationError(u'Date must be in future.')

    return cleaned_data

  def clean(self):
    cleaned_data = super(CouponForm, self).clean()

    if cleaned_data.get('duration') == 2 and cleaned_data.get('repeat_duration') == 0:
      self._errors['repeat_duration'] = u'You must specify a repeat duration greater than 0 if it is repeating.'
      # raise forms.ValidationError(u'You must specify a repeat duration greater than 0 if it is repeating.')

    if cleaned_data.get('amount_off') > 0 and cleaned_data.get('percent_off'):
      self._errors['amount_off'] = u'You can only set either amount off or percent off but not both.'
      self._errors['percent_off'] = u'You can only set either amount off or percent off but not both.'
      # raise forms.ValidationError(u'You can only set either amount off or percent off but not both.')

    if cleaned_data.get('amount_off') == 0 and cleaned_data.get('percent_off') == 0:
      self._errors['amount_off'] = u'You must set a value of 1 or more for either amount off or percent off.'
      self._errors['percent_off'] = u'You must set a value of 1 or more for either amount off or percent off.'
      # raise forms.ValidationError(u'You must set a value of 1 or more for either amount off or percent off.')

    return cleaned_data
