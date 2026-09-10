from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_deny

from products.models import Product


# ---- Vechile view-uri, server-rendered — păstrate pentru paginile ----
# ---- neconvertite încă la React (electric/acoustic/bass, dacă e cazul) ----

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