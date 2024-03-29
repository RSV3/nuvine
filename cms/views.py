# Create your views here.
from cms.models import ContentTemplate, Section
from cms.forms import EditSectionForm

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone


@staff_member_required
def template_list(request, type=0):
    data = {}
    page_num = request.GET.get('p', 0)
    templates = ContentTemplate.objects.filter(category=type, active=True).order_by('name', 'key')
    paginator = Paginator(templates, 10)
    try:
        page = paginator.page(page_num)
    except:
        page = paginator.page(1)

    data['page_count'] = paginator.num_pages
    data['page'] = page
    data['templates'] = page.object_list

    return render_to_response('cms/template_list.html', data, context_instance=RequestContext(request))


@staff_member_required
def edit_template(request, key):
    template = get_object_or_404(ContentTemplate, key=key)
    data = {}

    if request.method == 'GET':
        section = template.sections.all()[0]
        form = EditSectionForm(instance=section)
    else:
        if request.POST.get('section_select'):
            section = Section.objects.get(pk=request.POST.get('sections'))
            form = EditSectionForm(instance=section)
        else:
            section = Section.objects.get(pk=request.POST.get('sections'))
            form = EditSectionForm(request.POST or None, instance=section)

            if form.is_valid():
                form.save()
                template.last_modified = timezone.now()
                template.save()
                messages.success(request, "Template was successfully updated.")

    data['form'] = form
    data['template'] = template

    return render_to_response('cms/edit_template.html', data, context_instance=RequestContext(request))
