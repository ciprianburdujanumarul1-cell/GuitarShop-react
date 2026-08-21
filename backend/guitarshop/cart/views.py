import json
from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_deny

@xframe_options_deny
def cart_detail(request):

    cart = request.session.get('cart', {})
    
    items = []
    subtotal = Decimal('0.00')

    for product_id, qty in cart.items():
        product = get_object_or_404(Product, id=product_id)
        line_total = product.price * qty
        subtotal += line_total

        items.append({
            'product': product,
            'qty': qty,
            'line_total': line_total
        })

    vat = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'))
    total = subtotal + vat

    return render(request, 'cart.html', {
        'items': items,
        'subtotal': subtotal,
        'vat': vat,
        'total': total
    })
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    current_qty = cart.get(str(product_id), 0)
    print("CART RAW:", cart)
    print("STOCK:", product.stock)
    print("PRODUCT ID:", product_id)
    print("CURRENT QTY:", current_qty)
    if current_qty + 1 > product.stock:
        #return redirect('cart:cart_detail', id=product_id)
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
@transaction.atomic
@xframe_options_deny
def checkout(request):
    cart = request.session.get('cart', {})
    print("CHECKOUT CART:", cart)
    print("METHOD:", request.method)
    if request.method != 'POST':
        return redirect('cart:cart_detail')
    if not cart:
        return redirect('cart:cart_detail')

    products = []

    for product_id, qty in cart.items():
        try:
            product = Product.objects.select_for_update().get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Un produs din coș nu mai există.")
            return redirect('cart:cart_detail')

        if qty > product.stock:
            messages.error(request, f"Stoc insuficient pentru {product.name}.")
            return redirect('cart:cart_detail')

        products.append((product, qty))

    for product, qty in products:
        product.stock -= qty
        product.save(update_fields=['stock'])
    request.session['cart'] = {}
    messages.success(request, "Comandă plasată cu succes!")  # aici
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
