from django import forms
from django.contrib.auth.models import User, Group
from emailusernames.utils import create_user, create_superuser

from personality.models import Wine, WineRatingData

class WineRatingsForm(forms.ModelForm):

  class Meta:
    model = WineRatingData

class AllWineRatingsForm(forms.Form):
  first_name = forms.CharField(max_length=30)
  last_name = forms.CharField(max_length=30)
  email = forms.EmailField()

  wine1 = forms.IntegerField(widget=forms.HiddenInput())
  wine1_overall = forms.ChoiceField(label="Overall Rating", widget=forms.RadioSelect(attrs={"class":"radio"}), choices=WineRatingData.LIKENESS_CHOICES)
  wine1_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine1_sweet = forms.ChoiceField(label="Sweet", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES)
  wine1_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine1_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES)
  wine1_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine1_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES)
  wine1_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine1_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES)
  wine1_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)

  wine2 = forms.IntegerField(widget=forms.HiddenInput())
  wine2_overall = forms.ChoiceField(label="Overall Rating", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  wine2_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine2_sweet = forms.ChoiceField(label="Sweet", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES)
  wine2_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine2_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES)
  wine2_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine2_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES)
  wine2_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine2_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES)
  wine2_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)


  wine3 = forms.IntegerField(widget=forms.HiddenInput())
  wine3_overall = forms.ChoiceField(label="Overall Rating", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  wine3_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine3_sweet = forms.ChoiceField(label="Sweet", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES)
  wine3_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine3_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES)
  wine3_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine3_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES)
  wine3_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine3_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES)
  wine3_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)

  wine4 = forms.IntegerField(widget=forms.HiddenInput())
  wine4_overall = forms.ChoiceField(label="Overall Rating", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  wine4_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine4_sweet = forms.ChoiceField(label="Sweet", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES)
  wine4_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine4_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES)
  wine4_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine4_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES)
  wine4_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine4_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES)
  wine4_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)

  wine5 = forms.IntegerField(widget=forms.HiddenInput())
  wine5_overall = forms.ChoiceField(label="Overall Rating", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  wine5_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine5_sweet = forms.ChoiceField(label="Sweet", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES)
  wine5_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine5_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES)
  wine5_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine5_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES)
  wine5_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine5_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES)
  wine5_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)

  wine6 = forms.IntegerField(widget=forms.HiddenInput())
  wine6_overall = forms.ChoiceField(label="Overall Rating", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  wine6_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine6_sweet = forms.ChoiceField(label="Sweet", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES)
  wine6_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine6_weight = forms.ChoiceField(label="Weight", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES)
  wine6_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine6_texture = forms.ChoiceField(label="Texture", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES)
  wine6_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)
  wine6_sizzle = forms.ChoiceField(label="Sizzle", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES)
  wine6_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES)

  def save(self):

    results = []

    data = self.cleaned_data
    try:
      user = User.objects.get(email=data['email'])
    except User.DoesNotExist:
      # create new user
      user = create_user(email=data['email'], password='')
      user.first_name = data['first_name']
      user.last_name = data['last_name']
      user.save()

    results.append(user)

    # save each wine data
    for i in range(1,7):
      wine = Wine.objects.get(id=data['wine%d'%i])
      try:
        rating_data = WineRatingData.objects.get(user=user, wine=wine)
        # update
        rating_data.overall = data['wine%d_overall'%i]
        rating_data.dnl = data['wine%d_dnl'%i]
        rating_data.sweet = data['wine%d_sweet'%i]
        rating_data.sweet_dnl = data['wine%d_sweet_dnl'%i]
        rating_data.weight = data['wine%d_weight'%i]
        rating_data.weight_dnl = data['wine%d_weight_dnl'%i]
        rating_data.texture = data['wine%d_texture'%i]
        rating_data.texture_dnl = data['wine%d_texture_dnl'%i]
        rating_data.sizzle = data['wine%d_sizzle'%i]
        rating_data.sizzle_dnl = data['wine%d_sizzle_dnl'%i]
        rating_data.save()
      except WineRatingData.DoesNotExist:
        # create new data
        rating_data = WineRatingData.objects.create(
            user = user,
            wine = wine,
            overall = data['wine%d_overall'%i],
            dnl = data['wine%d_dnl'%i],
            sweet = data['wine%d_sweet'%i],
            sweet_dnl = data['wine%d_sweet_dnl'%i],
            weight = data['wine%d_weight'%i],
            weight_dnl = data['wine%d_weight_dnl'%i],
            texture = data['wine%d_texture'%i],
            texture_dnl = data['wine%d_texture_dnl'%i],
            sizzle = data['wine%d_sizzle'%i],
            sizzle_dnl = data['wine%d_sizzle_dnl'%i]
          )
      results.append(rating_data)

    # return user and all the 6 rating data objects
    return results
