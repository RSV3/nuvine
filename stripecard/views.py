# Create your views here.
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
import json

from stripecard.models import StripeCard

@require_POST
@csrf_exempt
def webhooks(request):
	stripe.api_key = settings.STRIPE_SECRET
	event_json = json.loads(HttpRequest.body)
	event = event_json['type']
	if event in HOOKS:
		hook = HOOKS[event]
		hook(event_json)
	return HttpResponse('sweet', status=200)

def invoice_created(event_json):
	data = event_json['data']['object']
	customer = data['customer']
	stripe_card = StripeCard.objects.get(stripe_user = customer)
	profile = stripe_card.stripe_owner.all()[0]
	my_plans = SubscriptionInfo.objects.filter(user=profile.user)
	# Order.objects.filter()
	# check what subscriptions are due
	# create invoice for these and send to stripe

HOOKS = {
	'invoice.created':invoice_created,
}

