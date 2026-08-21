import json
import logging

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from products.models import Product
from .models import StripeEvent

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Stripe calls this directly (no browser, no auth header), so it's a
    plain Django view outside DRF's JWT auth, exempt from CSRF like any
    webhook. Stock is decremented here — and only here — once payment is
    confirmed, so a closed browser tab or failed card never touches
    inventory.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if settings.STRIPE_WEBHOOK_SECRET and sig_header:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.warning("Invalid Stripe webhook signature: %s", e)
            return HttpResponse(status=400)
    else:
        # Local dev without `stripe listen --forward-to ... --print-secret`
        # configured yet — fall back to parsing the payload unverified.
        try:
            event = json.loads(payload)
        except ValueError:
            return HttpResponse(status=400)

    event_type = event['type']

    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session['id']

        # Idempotency: Stripe may retry the same event; only process once.
        _, created = StripeEvent.objects.get_or_create(session_id=session_id)
        if not created:
            return HttpResponse(status=200)

        metadata = session.get('metadata') if isinstance(session, dict) else session.to_dict().get('metadata', {})
        cart = json.loads(metadata.get('cart', '{}'))

        for product_id, qty in cart.items():
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                continue

            product.stock = max(product.stock - int(qty), 0)
            product.save(update_fields=['stock'])

    return HttpResponse(status=200)
