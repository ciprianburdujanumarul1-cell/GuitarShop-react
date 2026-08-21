import json
from decimal import Decimal

import stripe
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from products.models import Product, Wishlist
from .serializers import (
    ProductSerializer,
    ProductDetailSerializer,
    WishlistSerializer,
    RegisterSerializer,
    UserSerializer,
    EmailTokenObtainPairSerializer,
)


# ── AUTH ──────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Account created'}, status=status.HTTP_201_CREATED)


class EmailTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ── PRODUCTS ──────────────────────────────────────────

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        brand = self.kwargs['brand']
        qs = Product.objects.filter(brand=brand)
        shape = self.request.GET.get('shape', '')
        query = self.request.GET.get('q', '')
        if shape:
            qs = qs.filter(shape=shape)
        if query:
            qs = qs.filter(name__icontains=query)
        return qs

    def list(self, request, *args, **kwargs):
        brand = self.kwargs['brand']
        all_for_brand = Product.objects.filter(brand=brand)
        shapes = list(all_for_brand.values_list('shape', flat=True).distinct())
        response = super().list(request, *args, **kwargs)
        return Response({
            'brand': brand,
            'shapes': shapes,
            'selected': request.GET.get('shape', ''),
            'query': request.GET.get('q', ''),
            'products': response.data,
        })


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_url_kwarg = 'id'
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}


# ── WISHLIST ──────────────────────────────────────────

class WishlistListView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product').order_by('-created_at')


class ToggleWishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({'detail': 'Not found'}, status=404)

        item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            item.delete()
            favorited = False
        else:
            favorited = True

        count = Wishlist.objects.filter(user=request.user).count()
        return Response({'favorited': favorited, 'count': count})


# ── CART / CHECKOUT ───────────────────────────────────
# Cart itself lives client-side (localStorage); the backend only validates
# stock and finalises the order.

class CartQuoteView(APIView):
    """POST { items: {product_id: qty} } -> priced line items + totals."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = request.data.get('items', {})
        items = []
        subtotal = Decimal('0.00')

        for product_id, qty in cart.items():
            product = Product.objects.filter(id=product_id).first()
            if not product:
                continue
            qty = int(qty)
            line_total = product.price * qty
            subtotal += line_total
            items.append({
                'product': ProductSerializer(product, context={'request': request}).data,
                'qty': qty,
                'line_total': str(line_total),
            })

        vat = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'))
        total = subtotal + vat

        return Response({
            'items': items,
            'subtotal': str(subtotal),
            'vat': str(vat),
            'total': str(total),
        })


stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutView(APIView):
    """POST { items: {product_id: qty} } -> creates a Stripe Checkout Session
    and returns its hosted URL. Stock is only decremented once Stripe
    confirms payment (see payments.views.stripe_webhook) — not here — so an
    abandoned or failed payment never touches inventory."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = request.data.get('items', {})
        if not cart:
            return Response({'detail': 'Cart is empty'}, status=400)

        line_items = []
        cart_metadata = {}

        for product_id, qty in cart.items():
            qty = int(qty)
            product = Product.objects.filter(id=product_id).first()
            if not product:
                return Response({'detail': 'Un produs din coș nu mai există.'}, status=400)

            if qty > product.stock:
                return Response(
                    {'detail': f'Stoc insuficient pentru {product.name}.'},
                    status=400,
                )

            image_urls = []
            if product.image:
                image_urls = [request.build_absolute_uri(product.image.url)]

            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': product.name,
                        'images': image_urls,
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': qty,
            })
            cart_metadata[str(product.id)] = qty

        frontend_url = settings.FRONTEND_URL.rstrip('/')

        try:
            checkout_session = stripe.checkout.Session.create(
                mode='payment',
                payment_method_types=['card'],
                customer_email=request.user.email or None,
                line_items=line_items,
                success_url=f'{frontend_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{frontend_url}/checkout/cancel',
                metadata={
                    'user_id': str(request.user.id),
                    'cart': json.dumps(cart_metadata),
                },
            )
        except stripe.error.StripeError as e:
            return Response({'detail': f'Plata nu a putut fi inițiată: {e.user_message or str(e)}'}, status=400)

        return Response({'checkout_url': checkout_session.url})


class CheckoutSessionStatusView(APIView):
    """GET /api/checkout/session/<id>/ -> lets the success page confirm the
    payment actually went through (Stripe redirects the browser there
    regardless of outcome), and show an order summary."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError:
            return Response({'detail': 'Sesiune de plată invalidă.'}, status=404)
        metadata = session.to_dict().get('metadata', {})
        if metadata.get('user_id') != str(request.user.id):
            return Response({'detail': 'Not found'}, status=404)

        return Response({
            'payment_status': session.payment_status,  # 'paid' | 'unpaid' | 'no_payment_required'
            'amount_total': session.amount_total / 100 if session.amount_total is not None else None,
            'currency': session.currency,
            'customer_email': session.customer_details.email if session.customer_details else None,
        })
