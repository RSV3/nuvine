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

  def clean_redeem_by(self):
    cleaned_data = self.cleaned_data['redeem_by']
    today = timezone.now().date()

    if cleaned_data <= today:
      raise forms.ValidationError(u'Date must be in future')

    return cleaned_data

  def clean(self):
    cleaned_data = super(CouponForm, self).clean()

    if cleaned_data.get('amount_off') > 0 and cleaned_data.get('percent_off'):
      raise forms.ValidationError(u'You can only set either amount off or percent off but not both.')

    if cleaned_data.get('amount_off') == 0 and cleaned_data.get('percent_off') == 0:
      raise forms.ValidationError(u'You must set a value of 1 or more for either amount off or percent off.')

    if cleaned_data.get('duration') == 2 and cleaned_data.get('repeat_duration') == 0:
      raise forms.ValidationError(u'You must specify a repeat duration greater than 0 if it is repeating.')

    return cleaned_data
