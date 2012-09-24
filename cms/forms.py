from django import forms
from cms.models import ContentTemplate, Section
from django.forms import Textarea

class EditSectionForm(forms.ModelForm):
	sections = forms.ModelChoiceField(queryset=Section.objects.all()[:1], empty_label=None)

	def __init__(self, *args, **kwargs):
		super(EditSectionForm, self).__init__(*args, **kwargs)
		instance = kwargs.get('instance')
		if instance:
			sections = Section.objects.filter(template = instance.template)
			self.fields['sections'].queryset = Section.objects.filter(template = instance.template)
			self.fields['sections'].initial = instance

	class Meta:
		model = Section
		fields = ['sections', 'content']
		widgets = {'content':Textarea(attrs={'class':'span8', 'rows':20})}