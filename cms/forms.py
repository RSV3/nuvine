from django import forms
from cms.models import ContentTemplate, Section
from tinymce.widgets import TinyMCE


class EditSectionForm(forms.ModelForm):
  sections = forms.ModelChoiceField(queryset=Section.objects.all()[:1], empty_label=None)

  class Meta:
    model = Section
    fields = ['sections', 'content']
    widgets = {'content': TinyMCE(attrs={'class': 'span8', 'rows': 20}, mce_attrs={'theme': 'advanced', 'relative_urls': True})}

  def __init__(self, *args, **kwargs):
    super(EditSectionForm, self).__init__(*args, **kwargs)
    instance = kwargs.get('instance')
    if instance:
      sections = Section.objects.filter(template=instance.template)
      self.fields['sections'].queryset = Section.objects.filter(template=instance.template)
      self.fields['sections'].initial = instance

  def clean_content(self):
    cleaned = self.cleaned_data['content']
    return cleaned.replace('\r', '')
