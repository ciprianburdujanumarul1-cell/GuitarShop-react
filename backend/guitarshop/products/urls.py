from django.urls import path
from . import views
app_name = "products"
urlpatterns = [
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path("<str:brand>/", views.products_view, name="products_view"),
]