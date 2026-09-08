from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Vechile view-uri, server-rendered
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),

    # Noile endpoint-uri JSON, folosite de React Cart.jsx
    path('quote/', views.quote, name='quote'),
    path('checkout/', views.checkout, name='checkout'),
]