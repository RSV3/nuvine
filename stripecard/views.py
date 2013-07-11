# Create your views here.
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone

import stripe
import json
from main.models import Product, Cart
from accounts.models import SubscriptionInfo, Zipcode

from stripecard.models import StripeCard
from datetime import datetime, timedelta

import logging

log = logging.getLogger(__name__)


def shipping(plan):
    # Subscriptions get free shipping
    shipping = 0
    return shipping


def tax(sub_total, profile):
    if profile.shipping_address.state in Cart.NO_TAX_STATES:
        tax = 0
    else:
        if profile.shipping_address.state == 'CA':
            tax = float(sub_total) * 0.08
        else:
            tax = float(sub_total) * 0.06
    return tax


# deprecated
def subtotal(plan):
    if plan.quantity in [5, 6]:
        product = Product.objects.get(name="Basic Collection")
        return product.full_case_price if plan.quantity == 5 else product.unit_price
    elif plan.quantity in [7, 8]:
        product = Product.objects.get(name="Superior Collection")
        return product.full_case_price if plan.quantity == 7 else product.unit_price
    elif plan.quantity in [9, 10]:
        product = Product.objects.get(name="Divine Collection")
        return product.full_case_price if plan.quantity == 10 else product.unit_price
    else:
        return 0


@require_POST
@csrf_exempt
def webhooks(request):
    event_json = json.loads(request.raw_post_data)
    event = event_json['type']
    if event in HOOKS:
        hook = HOOKS[event]
        hook(event_json)
    return HttpResponse('sweet', status=200)


def invoice_created(event_json):
    from accounts.models import UserProfile
    data = event_json['data']['object']
    customer = data['customer']
    paid = data['paid']
    invoice_id = data['id']
    # print event_json
    if paid:
        # first time subscriptions are charged immediately
        # so for these, 'paid' will be true
        return

    # one-time purchases will not have a plan object within the data lines
    plan_found = None
    for item in data['lines']['data']:
        if item.get('plan'):
            plan_found = item['plan']
            break
    if plan_found is None:
        return

    # test webhook
    if event_json['id'] == 'evt_00000000000000':
        log.info('Running stripe test event: %s' % 'evt_00000000000000')
        data = event_json['data']['object']
        prof = UserProfile.objects.get(user__email='erik@mail.com')
        stripe_card = prof.stripe_card
    else:
        # TODO: Verify that this is actually from stripe
        try:
            stripe_card = StripeCard.objects.get(stripe_user=customer)
        except StripeCard.DoesNotExist:
            return

    profile = stripe_card.stripe_owner.all()[0]

    current_shipping = profile.shipping_address
    receiver_state = Zipcode.objects.get(code=current_shipping.zipcode).state

    if receiver_state == "MI":
        stripe.api_key = settings.STRIPE_SECRET
    elif receiver_state == "CA":
        stripe.api_key = settings.STRIPE_SECRET_CA

    # get latest subscription
    subscriptions = SubscriptionInfo.objects.filter(user=profile.user, frequency__in=[1, 2, 3]).order_by('-updated_datetime')
    if subscriptions.exists():
        subscription = subscriptions[0]
        sub_total = data['subtotal']
        # only need to add tax info
        stripe.InvoiceItem.create(customer=profile.stripe_card.stripe_user, amount=int(tax(sub_total, profile)), currency='usd', description='Tax')
        subscription.update_subscription_order(charge_stripe=False, invoice_id=invoice_id)


# NOTE: invoice_created_old below might be necessary once we allow multiple descriptions
def invoice_created_old(event_json):
    data = event_json['data']['object']
    customer = data['customer']
    # TODO: Verify that this is actually from stripe

    try:
        stripe_card = StripeCard.objects.get(stripe_user=customer)
    except StripeCard.DoesNotExist:
        return

    profile = stripe_card.stripe_owner.all()[0]

    # check what subscriptions are due
    # create invoice for these and send to stripe
    my_plans = SubscriptionInfo.objects.filter(user=profile.user, frequency__in=[1, 2, 3], next_invoice_date__lte=timezone.now().date())

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
            interval = 28 * plan.frequency
            next_invoice = datetime.date(datetime.now()) + timedelta(days=interval)
            plan.next_invoice_date = next_invoice
            plan.save()
        stripe.InvoiceItem.create(customer=profile.stripe_card.stripe_user, amount=int(shipping(my_plans) * 100), currency='usd', description='Shipping')
        stripe.InvoiceItem.create(customer=profile.stripe_card.stripe_user, amount=int(tax(total) * 100), currency='usd', description='Tax')

HOOKS = {
    'invoice.created': invoice_created,
}
