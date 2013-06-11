from django import forms
from coupon.models import Coupon
from main.models import Product


class CouponForm(forms.ModelForm):
  applies_to = forms.ModelMultipleChoiceField(queryset=Product.objects.filter(active=True).order_by('id'), widget=forms.CheckboxSelectMultiple)

  class Meta:
    model = Coupon
    exclude = ['created', 'updated']

  def __init__(self, *args, **kwargs):
    super(CouponForm, self).__init__(*args, **kwargs)
    self.fields['redeem_by'].widget.attrs['class'] = 'datepicker'
    # self.fields['applies_to'].queryset = Product.objects.filter(active=True)
    # self.fields['applies_to'].widget = forms.CheckboxSelectMultiple()
