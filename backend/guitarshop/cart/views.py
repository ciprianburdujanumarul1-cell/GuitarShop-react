import json
from decimal import Decimal

import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_deny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from products.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY

FRONTEND_URL = "http://localhost:5173"  # ajustează la portul tău Vite / .env


# ---- Vechile view-uri, server-rendered — păstrate pentru paginile ----
# ---- necovertite încă la React (electric/acoustic/bass, dacă e cazul) ----

@xframe_options_deny
def cart_detail(request):
    cart = request.session.get('cart', {})
    items = []
    subtotal = Decimal('0.00')

    for product_id, qty in cart.items():
        product = get_object_or_404(Product, id=product_id)
        line_total = product.price * qty
        subtotal += line_total
        items.append({'product': product, 'qty': qty, 'line_total': line_total})

    vat = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'))
    total = subtotal + vat

    return render(request, 'cart.html', {
        'items': items, 'subtotal': subtotal, 'vat': vat, 'total': total
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    current_qty = cart.get(str(product_id), 0)

    if current_qty + 1 > product.stock:
        return redirect('products:product_detail', id=product_id)

    cart[str(product_id)] = current_qty + 1
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart:cart_detail')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart:cart_detail')


def update_cart(request, product_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart = request.session.get('cart', {})
        key = str(product_id)
        if key in cart:
            if action == 'increase':
                cart[key] += 1
            elif action == 'decrease':
                cart[key] -= 1
                if cart[key] <= 0:
                    del cart[key]
        request.session['cart'] = cart
    return redirect('cart:cart_detail')


# ---- Noile view-uri JSON, folosite de React (Cart.jsx) ----

def _build_quote(items):
    """items: {'<product_id>': qty, ...} -> (listă items pentru răspuns, listă (product, qty), subtotal, vat, total)"""
    response_items = []
    checkout_items = []  # (product, qty) — separat, ca să nu trimitem obiecte Product spre JSON
    subtotal = Decimal('0.00')

    for product_id, qty in items.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        qty = max(int(qty), 1)
        line_total = (product.price * qty).quantize(Decimal('0.01'))
        subtotal += line_total

        response_items.append({
            'product': {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image': product.image.url if product.image else None,
            },
            'qty': qty,
            'line_total': str(line_total),
        })
        checkout_items.append((product, qty))

    vat = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'))
    total = (subtotal + vat).quantize(Decimal('0.01'))

    return response_items, checkout_items, subtotal.quantize(Decimal('0.01')), vat, total


@api_view(['POST'])
@permission_classes([AllowAny])
def quote(request):
    """Body: { "items": { "<product_id>": <qty>, ... } } — apelat de Cart.jsx la fiecare randare."""
    items = request.data.get('items', {})
    response_items, _, subtotal, vat, total = _build_quote(items)

    return Response({
        'items': response_items,
        'subtotal': str(subtotal),
        'vat': str(vat),
        'total': str(total),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def checkout(request):
    """
    Body: { "items": { "<product_id>": <qty>, ... } }
    Creează o sesiune Stripe Checkout și întoarce URL-ul ei.
    Stocul NU se atinge aici — doar webhook-ul (payments/views.py:
    stripe_webhook) scade stocul, după ce Stripe confirmă plata.
    """
    items = request.data.get('items', {})
    if not items:
        return Response({'detail': 'Coșul este gol.'}, status=400)

    _, checkout_items, subtotal, vat, total = _build_quote(items)
    if not checkout_items:
        return Response({'detail': 'Produse invalide în coș.'}, status=400)

    line_items = []
    for product, qty in checkout_items:
        if qty > product.stock:
            return Response({'detail': f'Stoc insuficient pentru {product.name}.'}, status=400)

        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': product.name,
                    'images': [request.build_absolute_uri(product.image.url)] if product.image else [],
                },
                'unit_amount': int(product.price * 100),
            },
            'quantity': qty,
        })

    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=line_items,
            metadata={'cart': json.dumps(items)},
            success_url=f'{FRONTEND_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{FRONTEND_URL}/checkout/cancel',
        )
    except stripe.error.StripeError as e:
        return Response({'detail': str(e)}, status=400)

    return Response({'checkout_url': session.url})