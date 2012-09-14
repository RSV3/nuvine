# Create your views here.
from cms.models import ContentTemplate, Variable
from cms.forms import EditTemplateForm

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

@staff_member_required
def template_list(request):
	data = {}
	data['templates'] = ContentTemplate.objects.all()
	return render_to_response('cms/template_list.html', data, context_instance=RequestContext(request))

@staff_member_required
def edit_template(request, key):
	template = get_object_or_404(ContentTemplate, key=key)
	data = {}
	form = EditTemplateForm(request.POST or None, instance=template)
	
	if form.is_valid():
		form.save()
	
	data['form'] = form
	data['template'] = template

	return render_to_response('cms/edit_template.html', data, context_instance=RequestContext(request))