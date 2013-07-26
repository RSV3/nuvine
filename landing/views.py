# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, Template, loader
from django.http import HttpResponse

def hello_world(request):
	
	data = {}
	todos = [ {'title': 'Mow the lawn', 'importance': 'Minor'},
	        {'title': 'Backup your PC', 'importance': 'High'},
	        {'title': 'Buy some Milk', 'importance': 'Medium'}, ]
	data['todos'] = todos
	return render_to_response("landing/landing.html", data, context_instance=RequestContext(request))

def invite(request):
	data = {}
	data['os'] = os = request.META['HTTP_USER_AGENT']
	data['get_mail'] = request.GET['mail']

	if os.find('Android') != -1 or os.find('iPhone') != -1 or os.find('iPad') != -1:
		# case of mobile
		return render_to_response("landing/mobile_landing.html", data, context_instance=RequestContext(request))

	else: #case of PC web
		return render_to_response("landing/web_landing.html", data, context_instance=RequestContext(request))