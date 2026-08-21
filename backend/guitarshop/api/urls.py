from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = 'api'

urlpatterns = [
    # auth
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.EmailTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/me/', views.MeView.as_view(), name='me'),

    # products
    path('products/<str:brand>/', views.ProductListView.as_view(), name='product_list'),
    path('products/detail/<int:id>/', views.ProductDetailView.as_view(), name='product_detail'),

    # wishlist
    path('wishlist/', views.WishlistListView.as_view(), name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.ToggleWishlistView.as_view(), name='toggle_wishlist'),

    # cart / stripe checkout
    path('cart/quote/', views.CartQuoteView.as_view(), name='cart_quote'),
    path('cart/checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/session/<str:session_id>/', views.CheckoutSessionStatusView.as_view(), name='checkout_session_status'),
]
