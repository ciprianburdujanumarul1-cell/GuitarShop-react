import stripe
import os
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from products.models import Product
from django.http import JsonResponse

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)

        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': product.name,
                        'images': [request.build_absolute_uri(product.image.url)],
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': 1,
            }],
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
        )

        return redirect(session.url)

    except Exception as e:
        return JsonResponse({'error': str(e)})