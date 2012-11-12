from django import forms
from django.contrib.auth.models import User, Group
from emailusernames.utils import create_user, create_superuser
from django.utils import timezone
from main.models import PartyInvite

from personality.models import Wine, WineRatingData, GeneralTaste, WineTaste, SurveyWine

class WineRatingsForm(forms.ModelForm):

  class Meta:
    model = WineRatingData

class AddTasterRatingsForm(forms.ModelForm):
  first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
  last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
  email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))

  class Meta:
    model = User
    exclude = ['username', 'password', 'last_login', 'date_joined']

  def clean(self):
    cleaned_data = super(AddTasterRatingsForm, self).clean()

    if 'email' in cleaned_data:
      cleaned_data['email'] = cleaned_data['email'].strip().lower()

    return cleaned_data


from django.utils.safestring import mark_safe
class CustomRadioField(forms.RadioSelect.renderer):
  def render(self):
    items = []
    labels = []
    for x in self:
      if x.index == 0:
        items.append('')
        labels.append('')
      else:
        radio_html = '''
          <div class="span1">
            <center>
              <input type="radio" id="%s" value="%s" name="%s" %s />
            </center>
          </div>
        ''' % (x.attrs['id'], x.index, x.name, 'checked="checked"' if x.is_checked() else "")

        items.append(radio_html)

        if x.index == 1 or x.index == 5 or \
          (x.index == 3 and ('weight' in x.name or 'sizzle' in x.name)) or \
          ('overall' in x.name):
          label_html = '''
            <div class="span1">
              <center>
                <label>%s</label>
              </center>
            </div>
          ''' % x.choice_label
        else:
          label_html = '<div class="span1">&nbsp;</div>'
        labels.append(label_html)

    return mark_safe(u'\n'.join(items) + u'\n'.join(labels))


class AllWineRatingsForm(forms.Form):
  # first_name = forms.CharField(widget=forms.HiddenInput())
  # last_name = forms.CharField(widget=forms.HiddenInput())
  email = forms.EmailField(widget=forms.HiddenInput())

  wine1 = forms.IntegerField(widget=forms.HiddenInput())
  wine1_overall = forms.ChoiceField(label="Feeling", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.LIKENESS_CHOICES, initial=0, required=False)
  #wine1_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine1_sweet = forms.ChoiceField(label="Sweetness", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SWEET_CHOICES, initial=0, required=False)
  wine1_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine1_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.WEIGHT_CHOICES, initial=0, required=False)
  wine1_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine1_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.TEXTURE_CHOICES, initial=0, required=False)
  wine1_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine1_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SIZZLE_CHOICES, initial=0, required=False)
  wine1_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)

  wine2 = forms.IntegerField(widget=forms.HiddenInput())
  wine2_overall = forms.ChoiceField(label="Feeling", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.LIKENESS_CHOICES, initial=0, required=False)
  #wine2_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine2_sweet = forms.ChoiceField(label="Sweetness", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SWEET_CHOICES, initial=0, required=False)
  wine2_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine2_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.WEIGHT_CHOICES, initial=0, required=False)
  wine2_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine2_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.TEXTURE_CHOICES, initial=0, required=False)
  wine2_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine2_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SIZZLE_CHOICES, initial=0, required=False)
  wine2_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)


  wine3 = forms.IntegerField(widget=forms.HiddenInput())
  wine3_overall = forms.ChoiceField(label="Feeling", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.LIKENESS_CHOICES, initial=0, required=False)
  #wine3_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine3_sweet = forms.ChoiceField(label="Sweetness", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SWEET_CHOICES, initial=0, required=False)
  wine3_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine3_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.WEIGHT_CHOICES, initial=0, required=False)
  wine3_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine3_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.TEXTURE_CHOICES, initial=0, required=False)
  wine3_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine3_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SIZZLE_CHOICES, initial=0, required=False)
  wine3_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)

  wine4 = forms.IntegerField(widget=forms.HiddenInput())
  wine4_overall = forms.ChoiceField(label="Feeling", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.LIKENESS_CHOICES, initial=0, required=False)
  #wine4_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine4_sweet = forms.ChoiceField(label="Sweetness", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SWEET_CHOICES, initial=0, required=False)
  wine4_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine4_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.WEIGHT_CHOICES, initial=0, required=False)
  wine4_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine4_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.TEXTURE_CHOICES, initial=0, required=False)
  wine4_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine4_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SIZZLE_CHOICES, initial=0, required=False)
  wine4_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)

  wine5 = forms.IntegerField(widget=forms.HiddenInput())
  wine5_overall = forms.ChoiceField(label="Feeling", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.LIKENESS_CHOICES, initial=0, required=False)
  #wine5_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine5_sweet = forms.ChoiceField(label="Sweetness", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SWEET_CHOICES, initial=0, required=False)
  wine5_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine5_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.WEIGHT_CHOICES, initial=0, required=False)
  wine5_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine5_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.TEXTURE_CHOICES, initial=0, required=False)
  wine5_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine5_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SIZZLE_CHOICES, initial=0, required=False)
  wine5_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)

  wine6 = forms.IntegerField(widget=forms.HiddenInput())
  wine6_overall = forms.ChoiceField(label="Feeling", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.LIKENESS_CHOICES, initial=0, required=False)
  #wine6_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine6_sweet = forms.ChoiceField(label="Sweetness", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SWEET_CHOICES, initial=0, required=False)
  wine6_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine6_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.WEIGHT_CHOICES, initial=0, required=False)
  wine6_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine6_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.TEXTURE_CHOICES, initial=0, required=False)
  wine6_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)
  wine6_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect(renderer=CustomRadioField), choices=WineRatingData.SIZZLE_CHOICES, initial=0, required=False)
  wine6_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0, required=False)

  def save(self):

    results = []
    
    data = self.cleaned_data
    user = User.objects.get(email=data['email'])
    results.append(user)

    # save each wine data
    for i in range(1, 7):
      wine = Wine.objects.get(id=data['wine%d' % i])
      try:
        rating_data = WineRatingData.objects.get(user=user, wine=wine)
        # update
        rating_data.overall = int(data['wine%d_overall' % i])         if data['wine%d_overall' % i] else 0
        #rating_data.dnl = int(data['wine%d_dnl'%i])
        rating_data.sweet = int(data['wine%d_sweet' % i])             if data['wine%d_sweet' % i] else 0
        rating_data.sweet_dnl = int(data['wine%d_sweet_dnl' % i])     if data['wine%d_sweet_dnl' % i] else 0
        rating_data.weight = int(data['wine%d_weight' % i])           if data['wine%d_weight' % i] else 0
        rating_data.weight_dnl = int(data['wine%d_weight_dnl' % i])   if data['wine%d_weight_dnl' % i] else 0
        rating_data.texture = int(data['wine%d_texture' % i])         if data['wine%d_texture' % i] else 0
        rating_data.texture_dnl = int(data['wine%d_texture_dnl' % i]) if data['wine%d_texture_dnl' % i] else 0
        rating_data.sizzle = int(data['wine%d_sizzle' % i])           if data['wine%d_sizzle' % i] else 0
        rating_data.sizzle_dnl = int(data['wine%d_sizzle_dnl' % i])   if data['wine%d_sizzle_dnl' % i] else 0
        rating_data.save()
      except WineRatingData.DoesNotExist:
        # create new data
        rating_data = WineRatingData.objects.create(
            user = user,
            wine = wine,
            overall = int(data['wine%d_overall' % i])        if data['wine%d_overall' % i] else 0,
            #dnl = int(data['wine%d_dnl'%i]),
            sweet = int(data['wine%d_sweet' % i])             if data['wine%d_sweet' % i] else 0,
            sweet_dnl = int(data['wine%d_sweet_dnl' % i])     if data['wine%d_sweet_dnl' % i] else 0,
            weight = int(data['wine%d_weight' % i])           if data['wine%d_weight' % i] else 0,
            weight_dnl = int(data['wine%d_weight_dnl' % i])   if data['wine%d_weight_dnl' % i] else 0,
            texture = int(data['wine%d_texture' % i])         if data['wine%d_texture' % i] else 0,
            texture_dnl = int(data['wine%d_texture_dnl' % i]) if data['wine%d_texture_dnl' % i] else 0,
            sizzle = int(data['wine%d_sizzle' % i])           if data['wine%d_sizzle' % i] else 0,
            sizzle_dnl = int(data['wine%d_sizzle_dnl' % i])   if data['wine%d_sizzle_dnl' % i] else 0
          )
      results.append(rating_data)

    # return user and all the 6 rating data objects
    return results

class GeneralTasteQuestionnaire(forms.ModelForm):

  class Meta:
    model = GeneralTaste

  def __init__(self, *args, **kwargs):
    super(GeneralTasteQuestionnaire, self).__init__(*args, **kwargs)
    self.fields['user'].widget = forms.HiddenInput()
    self.fields['drink_regularly'].widget = forms.RadioSelect(choices=GeneralTaste.DRINK_REGULAR_CHOICES)
    self.fields['coffee_type'].widget = forms.RadioSelect(choices=GeneralTaste.COFFEE_CHOICES)
    self.fields['coffee_take'].widget = forms.RadioSelect(choices=GeneralTaste.COFFEE_TAKE_CHOICES)
    self.fields['salty_food'].widget = forms.RadioSelect(choices=GeneralTaste.SALTY_FOOD_CHOICES)
    self.fields['citrus'].widget = forms.RadioSelect(choices=GeneralTaste.CITRUS_CHOICES)
    self.fields['earthy'].widget = forms.RadioSelect(choices=GeneralTaste.EARTHY_CHOICES)
    self.fields['berries'].widget = forms.RadioSelect(choices=GeneralTaste.BERRIES_CHOICES)
    self.fields['artificial'].widget = forms.RadioSelect(choices=GeneralTaste.ARTIFICIAL_CHOICES)
    self.fields['new_flavors'].widget = forms.RadioSelect(choices=GeneralTaste.NEW_FLAVORS_CHOICES)

class WineTasteQuestionnaire(forms.ModelForm):

  red_survey_wines = SurveyWine.objects.filter(color=SurveyWine.COLOR_CHOICES[0][0])
  select_choices = [(s.id, s.name) for s in red_survey_wines] + [(red_survey_wines.count() + 1, 'Other')]
  red_wines_often = forms.MultipleChoiceField(choices=select_choices, required=False, widget=forms.CheckboxSelectMultiple, label='What RED wine(s) do you currently drink most often? (select up to 2)')
  red_wine_dislike = forms.ChoiceField(choices=select_choices, required=False, widget=forms.RadioSelect, label='What RED wine, if any, do you particularly DISLIKE? (select one, optional)')

  white_survey_wines = SurveyWine.objects.filter(color=SurveyWine.COLOR_CHOICES[1][0])
  select_choices = [(s.id, s.name) for s in white_survey_wines] + [(white_survey_wines.count() + 1, 'Other')]
  white_wines_often = forms.MultipleChoiceField(choices=select_choices, required=False, widget=forms.CheckboxSelectMultiple, label='What WHITE wine(s) do you currently drink most often? (select up to 2)')
  white_wine_dislike = forms.ChoiceField(choices=select_choices, required=False, widget=forms.RadioSelect, label='What WHITE wine, if any, do you particularly DISLIKE? (select one, optional)')
  other_wines = forms.ModelMultipleChoiceField(queryset=SurveyWine.objects.filter(color=SurveyWine.COLOR_CHOICES[2][0]), required=False, widget=forms.CheckboxSelectMultiple, label='Do you drink (select all that apply):')

  class Meta:
    model = WineTaste
    exclude = ['red_acidity', 'white_acidity']

  def __init__(self, *args, **kwargs):
    super(WineTasteQuestionnaire, self).__init__(*args, **kwargs)
    self.fields['user'].widget = forms.HiddenInput()
    self.fields['typically_drink'].widget = forms.RadioSelect(choices=WineTaste.TYPICALLY_DRINK_CHOICES)
    self.fields['red_body'].widget = forms.RadioSelect(attrs={'class': 'horizontal-radio'}, choices=WineTaste.RED_BODY_CHOICES)
    self.fields['red_sweetness'].widget = forms.RadioSelect(choices=WineTaste.RED_SWEETNESS_CHOICES)
    #self.fields['red_acidity'].widget = forms.RadioSelect(choices=WineTaste.RED_ACIDITY_CHOICES)
    self.fields['red_color'].widget = forms.RadioSelect(choices=WineTaste.RED_COLOR_CHOICES)
    self.fields['white_oak'].widget = forms.RadioSelect(choices=WineTaste.WHITE_OAK_CHOICES)
    self.fields['white_sweetness'].widget = forms.RadioSelect(choices=WineTaste.WHITE_SWEETNESS_CHOICES)
    #self.fields['white_acidity'].widget = forms.RadioSelect(choices=WineTaste.WHITE_ACIDITY_CHOICES)
    self.fields['white_color'].widget = forms.RadioSelect(choices=WineTaste.WHITE_COLOR_CHOICES)

  def clean(self):
    cleaned_data = super(WineTasteQuestionnaire, self).clean()

    wine_id = cleaned_data['red_wine_dislike']
    if wine_id:
      cleaned_data['red_wine_dislike'] = SurveyWine.objects.get(id=wine_id)
    else:
      cleaned_data['red_wine_dislike'] = None
    wine_id = cleaned_data['white_wine_dislike']
    if wine_id:
      cleaned_data['white_wine_dislike'] = SurveyWine.objects.get(id=wine_id)
    else:
      cleaned_data['white_wine_dislike'] = None

    return cleaned_data

