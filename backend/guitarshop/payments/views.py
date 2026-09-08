# payments/views.py
import json
import logging

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from products.models import Product
from .models import StripeEvent

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@require_POST
def stripe_webhook(request):
    # ... rămâne exact cum era la tine, neschimbat ...
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if settings.STRIPE_WEBHOOK_SECRET and sig_header:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.warning("Invalid Stripe webhook signature: %s", e)
            return HttpResponse(status=400)
    else:
        try:
            event = json.loads(payload)
        except ValueError:
            return HttpResponse(status=400)

    event_type = event['type']

    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session['id']

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


@api_view(['GET'])
@permission_classes([AllowAny])
def session_status(request, session_id):
    """Apelat de CheckoutSuccess.jsx ca să confirme plata după redirect de la Stripe."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError as e:
        return Response({'detail': str(e)}, status=400)

    return Response({
        'payment_status': session.payment_status,
        'customer_email': session.customer_details.email if session.customer_details else None,
        'amount_total': session.amount_total / 100 if session.amount_total is not None else None,
        'currency': session.currency,
    })