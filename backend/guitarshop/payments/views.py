# payments/views.py
import json
import logging

import stripe
from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from products.models import Product
from orders.models import Order  # <- nou, modelul de comandă

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Schimbare 1: nu mai există fallback fără verificare de semnătură.
    # Fără STRIPE_WEBHOOK_SECRET configurat, endpoint-ul refuză cererea în
    # loc să accepte orice JSON ca eveniment Stripe valid.
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET is not configured — refusing webhook.")
        return HttpResponse(status=500)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.warning("Invalid Stripe webhook signature: %s", e)
        return HttpResponse(status=400)

    event_type = event['type']

    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        session_dict = session.to_dict() if hasattr(session, 'to_dict') else session
        session_id = session_dict['id']

        if Order.objects.filter(stripe_session_id=session_id).exists():
            return HttpResponse(status=200)

        metadata = session_dict.get('metadata', {})
        cart = json.loads(metadata.get('cart', '{}'))
        address = json.loads(metadata.get('address', '{}'))

        for product_id, qty in cart.items():
            Product.objects.filter(id=product_id).update(stock=F('stock') - int(qty))

        Order.objects.create(
            user_id=metadata.get('user_id'),
            stripe_session_id=session_id,
            items=cart,
            full_name=address.get('fullName', ''),
            address_line1=address.get('line1', ''),
            address_line2=address.get('line2', ''),
            city=address.get('city', ''),
            postal_code=address.get('postalCode', ''),
            country=metadata.get('country', ''),
            vat_rate=metadata.get('vat_rate', '0'),
            amount_total=(session_dict.get('amount_total') or 0) / 100,
        )

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