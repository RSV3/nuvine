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
  wine1_overall = forms.ChoiceField(label="Feeling Factor", widget=forms.RadioSelect(attrs={"class":"radio"}), choices=WineRatingData.LIKENESS_CHOICES)
  #wine1_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine1_sweet = forms.ChoiceField(label="Sweetness Factor", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES, initial=0)
  wine1_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine1_weight = forms.ChoiceField(label="Weight Factor", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES, initial=0)
  wine1_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine1_texture = forms.ChoiceField(label="Texture Factor", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES, initial=0)
  wine1_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine1_sizzle = forms.ChoiceField(label="Sizzle Factor", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES, initial=0)
  wine1_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)

  wine2 = forms.IntegerField(widget=forms.HiddenInput())
  wine2_overall = forms.ChoiceField(label="Feeling Factor", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  #wine2_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine2_sweet = forms.ChoiceField(label="Sweetness Factor", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES, initial=0)
  wine2_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine2_weight = forms.ChoiceField(label="Weight Factor", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES, initial=0)
  wine2_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine2_texture = forms.ChoiceField(label="Texture Factor", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES, initial=0)
  wine2_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine2_sizzle = forms.ChoiceField(label="Sizzle Factor", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES, initial=0)
  wine2_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)


  wine3 = forms.IntegerField(widget=forms.HiddenInput())
  wine3_overall = forms.ChoiceField(label="Feeling Factor", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  #wine3_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine3_sweet = forms.ChoiceField(label="Sweetness Factor", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES, initial=0)
  wine3_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine3_weight = forms.ChoiceField(label="Weight Factor", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES, initial=0)
  wine3_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine3_texture = forms.ChoiceField(label="Texture Factor", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES, initial=0)
  wine3_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine3_sizzle = forms.ChoiceField(label="Sizzle Factor", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES, initial=0)
  wine3_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)

  wine4 = forms.IntegerField(widget=forms.HiddenInput())
  wine4_overall = forms.ChoiceField(label="Feeling Factor", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  #wine4_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine4_sweet = forms.ChoiceField(label="Sweetness Factor", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES, initial=0)
  wine4_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine4_weight = forms.ChoiceField(label="Weight Factor", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES, initial=0)
  wine4_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine4_texture = forms.ChoiceField(label="Texture Factor", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES, initial=0)
  wine4_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine4_sizzle = forms.ChoiceField(label="Sizzle Factor", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES, initial=0)
  wine4_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)

  wine5 = forms.IntegerField(widget=forms.HiddenInput())
  wine5_overall = forms.ChoiceField(label="Feeling Factor", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  #wine5_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine5_sweet = forms.ChoiceField(label="Sweetness Factor", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES, initial=0)
  wine5_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine5_weight = forms.ChoiceField(label="Weight Factor", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES, initial=0)
  wine5_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine5_texture = forms.ChoiceField(label="Texture Factor", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES, initial=0)
  wine5_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine5_sizzle = forms.ChoiceField(label="Sizzle Factor", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES, initial=0)
  wine5_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)

  wine6 = forms.IntegerField(widget=forms.HiddenInput())
  wine6_overall = forms.ChoiceField(label="Feeling Factor", widget=forms.RadioSelect, choices=WineRatingData.LIKENESS_CHOICES)
  #wine6_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine6_sweet = forms.ChoiceField(label="Sweetness Factor", widget=forms.RadioSelect, choices=WineRatingData.SWEET_CHOICES, initial=0)
  wine6_sweet_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine6_weight = forms.ChoiceField(label="Weight Factor", widget=forms.RadioSelect, choices=WineRatingData.WEIGHT_CHOICES, initial=0)
  wine6_weight_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine6_texture = forms.ChoiceField(label="Texture Factor", widget=forms.RadioSelect, choices=WineRatingData.TEXTURE_CHOICES, initial=0)
  wine6_texture_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)
  wine6_sizzle = forms.ChoiceField(label="Sizzle Factor", widget=forms.RadioSelect, choices=WineRatingData.SIZZLE_CHOICES, initial=0)
  wine6_sizzle_dnl = forms.ChoiceField(label="Like It?", widget=forms.RadioSelect, choices=WineRatingData.DNL_CHOICES, initial=0)

  def save(self):

    results = []

    data = self.cleaned_data
    try:
      user = User.objects.get(email=data['email'].lower())
    except User.DoesNotExist:
      # create new user
      user = create_user(email=data['email'].lower(), password='welcome')
      user.first_name = data['first_name']
      user.last_name = data['last_name']
      user.save()

      if user.groups.all().count() == 0:
        # add to attendee group
        attendee_group = Group.objects.get(name="Attendee")
        user.groups.add(attendee_group)
        user.save()

    results.append(user)

    # save each wine data
    for i in range(1,7):
      wine = Wine.objects.get(id=data['wine%d'%i])
      try:
        rating_data = WineRatingData.objects.get(user=user, wine=wine)
        # update
        rating_data.overall = int(data['wine%d_overall'%i])
        #rating_data.dnl = int(data['wine%d_dnl'%i])
        rating_data.sweet = int(data['wine%d_sweet'%i])
        rating_data.sweet_dnl = int(data['wine%d_sweet_dnl'%i])
        rating_data.weight = int(data['wine%d_weight'%i])
        rating_data.weight_dnl = int(data['wine%d_weight_dnl'%i])
        rating_data.texture = int(data['wine%d_texture'%i])
        rating_data.texture_dnl = int(data['wine%d_texture_dnl'%i])
        rating_data.sizzle = int(data['wine%d_sizzle'%i])
        rating_data.sizzle_dnl = int(data['wine%d_sizzle_dnl'%i])
        rating_data.save()
      except WineRatingData.DoesNotExist:
        # create new data
        rating_data = WineRatingData.objects.create(
            user = user,
            wine = wine,
            overall = int(data['wine%d_overall'%i]),
            #dnl = int(data['wine%d_dnl'%i]),
            sweet = int(data['wine%d_sweet'%i]),
            sweet_dnl = int(data['wine%d_sweet_dnl'%i]),
            weight = int(data['wine%d_weight'%i]),
            weight_dnl = int(data['wine%d_weight_dnl'%i]),
            texture = int(data['wine%d_texture'%i]),
            texture_dnl = int(data['wine%d_texture_dnl'%i]),
            sizzle = int(data['wine%d_sizzle'%i]),
            sizzle_dnl = int(data['wine%d_sizzle_dnl'%i])
          )
      results.append(rating_data)

    # return user and all the 6 rating data objects
    return results
