# cart/context_processors.py

def cart_count(request):
    cart = request.session.get('cart', {})
    total = sum(cart.values())
    return {'cart_count': total}