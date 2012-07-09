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
  wine1 = forms.IntegerField()
  wine1_overall = forms.IntegerField()
  wine1_dnl = forms.IntegerField()
  wine1_sweet = forms.IntegerField()
  wine1_sweet_dnl = forms.IntegerField()
  wine1_weight = forms.IntegerField()
  wine1_weight_dnl = forms.IntegerField()
  wine1_texture = forms.IntegerField()
  wine1_texture_dnl = forms.IntegerField()
  wine1_sizzle = forms.IntegerField()
  wine1_sizzle_dnl = forms.IntegerField()
  wine2 = forms.IntegerField()
  wine2_overall = forms.IntegerField()
  wine2_dnl = forms.IntegerField()
  wine2_sweet = forms.IntegerField()
  wine2_sweet_dnl = forms.IntegerField()
  wine2_weight = forms.IntegerField()
  wine2_weight_dnl = forms.IntegerField()
  wine2_texture = forms.IntegerField()
  wine2_texture_dnl = forms.IntegerField()
  wine2_sizzle = forms.IntegerField()
  wine2_sizzle_dnl = forms.IntegerField()
  wine3 = forms.IntegerField()
  wine3_overall = forms.IntegerField()
  wine3_dnl = forms.IntegerField()
  wine3_sweet = forms.IntegerField()
  wine3_sweet_dnl = forms.IntegerField()
  wine3_weight = forms.IntegerField()
  wine3_weight_dnl = forms.IntegerField()
  wine3_texture = forms.IntegerField()
  wine3_texture_dnl = forms.IntegerField()
  wine3_sizzle = forms.IntegerField()
  wine3_sizzle_dnl = forms.IntegerField()
  wine4 = forms.IntegerField()
  wine4_overall = forms.IntegerField()
  wine4_dnl = forms.IntegerField()
  wine4_sweet = forms.IntegerField()
  wine4_sweet_dnl = forms.IntegerField()
  wine4_weight = forms.IntegerField()
  wine4_weight_dnl = forms.IntegerField()
  wine4_texture = forms.IntegerField()
  wine4_texture_dnl = forms.IntegerField()
  wine4_sizzle = forms.IntegerField()
  wine4_sizzle_dnl = forms.IntegerField()
  wine5 = forms.IntegerField()
  wine5_overall = forms.IntegerField()
  wine5_dnl = forms.IntegerField()
  wine5_sweet = forms.IntegerField()
  wine5_sweet_dnl = forms.IntegerField()
  wine5_weight = forms.IntegerField()
  wine5_weight_dnl = forms.IntegerField()
  wine5_texture = forms.IntegerField()
  wine5_texture_dnl = forms.IntegerField()
  wine5_sizzle = forms.IntegerField()
  wine5_sizzle_dnl = forms.IntegerField()
  wine6 = forms.IntegerField()
  wine6_overall = forms.IntegerField()
  wine6_dnl = forms.IntegerField()
  wine6_sweet = forms.IntegerField()
  wine6_sweet_dnl = forms.IntegerField()
  wine6_weight = forms.IntegerField()
  wine6_weight_dnl = forms.IntegerField()
  wine6_texture = forms.IntegerField()
  wine6_texture_dnl = forms.IntegerField()
  wine6_sizzle = forms.IntegerField()
  wine6_sizzle_dnl = forms.IntegerField()

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
