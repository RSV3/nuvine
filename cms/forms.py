from django import forms
from cms.models import ContentTemplate


class EditTemplateForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(EditTemplateForm, self).__init__(*args, **kwargs)
		self.fields['content'].widget.attrs = {'class':'span8', 'rows':20}

	class Meta:
			model = ContentTemplate
			fields = ['content']