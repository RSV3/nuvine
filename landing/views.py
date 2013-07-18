# Create your views here.
from django.template import Context, loader
from django.http import HttpResponse

def hello_world(request):
    todos = [ {'title': 'Mow the lawn', 'importance': 'Minor'},
              {'title': 'Backup your PC', 'importance': 'High'},
              {'title': 'Buy some Milk', 'importance': 'Medium'}, ]
    t = loader.get_template('landing.html')
    c = Context({ 'todos': todos, })
    return HttpResponse(t.render(c))

def invite(request):
    os = request.META['HTTP_USER_AGENT']
    get_mail = request.GET['mail']
    t = loader.get_template('invite.html')
    c = Context({
      'os' : os,
      'get_mail' : get_mail,
    })
    return HttpResponse(t.render(c))