from django.shortcuts import render, get_object_or_404
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Product, Review, Wishlist
from django.http import JsonResponse
from django.views.decorators.http import require_POST

admin.site.register(Product)
admin.site.register(Review)



@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        item.delete()
        favorited = False
    else:
        favorited = True

    count = Wishlist.objects.filter(user=request.user).count()

    return JsonResponse({'favorited': favorited, 'count': count})
@login_required
def products_view(request, brand):

    products = Product.objects.filter(brand=brand)
    shapes = products.values_list('shape', flat=True).distinct()

    shape = request.GET.get('shape', '')
    query = request.GET.get('q', '')

    if shape:
        products = products.filter(shape=shape)
    if query:
        products = products.filter(name__icontains=query)

    return render(request, "products.html", {
        "products": products,
        "brand": brand,
        "shapes": shapes,
        "selected": shape,
        "query": query,
    })

@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    reviews = product.reviews.order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    is_favorited = Wishlist.objects.filter(user=request.user, product=product).exists()
    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return render(request, "Produs.html", {
        "product": product,
        "reviews": reviews,
        "avg_rating": round(avg_rating, 1) if avg_rating else None,
        "review_count": reviews.count(),
        "is_favorited": is_favorited,
        "wishlist_count": wishlist_count,
    })
# views.py
@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product').order_by('-created_at')

    return render(request, "wishlist.html", {
        "wishlist_items": wishlist_items,
    })