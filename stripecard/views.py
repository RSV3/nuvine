# Create your views here.
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone

import stripe
import json
from main.models import LineItem, Product
from accounts.models import SubscriptionInfo
from stripecard.models import StripeCard

def shipping(plans):
	# TODO: check invoice qty
  shipping = 0
  for item in xrange(plans.count()):
    # always $16 - August 2, 2012
    shipping += 16
  return shipping 

def tax(sub_total):
  # TODO: tax needs to be calculated based on the state
  tax = float(sub_total)*0.06
  return tax 

def subtotal(plan):
	if plan.quantity in [5,6]:
		product = Product.objects.get(name = "Basic Collection")
		return product.full_case_price if plan.quantity == 5 else product.unit_price
	elif plan.quantity in [7,8]:
		product = Product.objects.get(name = "Superior Collection")
		return product.full_case_price if plan.quantity == 7 else product.unit_price		
	elif plan.quantity in [9,10]:
		product = Product.objects.get(name = "Divine Collection")
		return product.full_case_price if plan.quantity == 10 else product.unit_price		
	else:
		return 0

@require_POST
@csrf_exempt
def webhooks(request):
	stripe.api_key = settings.STRIPE_SECRET
	event_json = json.loads(request.raw_post_data)
	event = event_json['type']
	if event in HOOKS:
		hook = HOOKS[event]
		hook(event_json)
	return HttpResponse('sweet', status=200)

def invoice_created(event_json):
	data = event_json['data']['object']
	customer = data['customer']
	# TODO: Verify that this is actually from stripe

	try:
		stripe_card = StripeCard.objects.get(stripe_user = customer)
	except StripeCard.DoesNotExist:
		return

	profile = stripe_card.stripe_owner.all()[0]

	# check what subscriptions are due
	# create invoice for these and send to stripe
	my_plans = SubscriptionInfo.objects.filter(user=profile.user, frequency__in = [1,2,3], next_invoice_date__lte = timezone.now().date())

	# charge card to stripe
	stripe.api_key = settings.STRIPE_SECRET

	if my_plans.exists():
		total = sub_total = 0
		qty = dict(SubscriptionInfo.QUANTITY_CHOICES)
		freq = dict(SubscriptionInfo.FREQUENCY_CHOICES)

		for plan in my_plans:
			sub_total = subtotal(plan)
			total += sub_total
			plan_desc = ("%s subscription -  %s" % (freq[plan.frequency], qty[plan.quantity]))
			stripe.InvoiceItem.create(customer=profile.stripe_card.stripe_user, amount=int(sub_total * 100), currency='usd', description=plan_desc)

		stripe.InvoiceItem.create(customer=profile.stripe_card.stripe_user, amount=int(shipping(my_plans) * 100), currency='usd', description='Shipping')
		stripe.InvoiceItem.create(customer=profile.stripe_card.stripe_user, amount=int(tax(total) * 100), currency='usd', description='Tax')

HOOKS = {
	'invoice.created':invoice_created,
}

