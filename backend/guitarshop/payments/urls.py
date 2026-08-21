from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Stripe webhook — confirms payment and decrements stock.
    # Configure in the Stripe Dashboard (or `stripe listen`) as:
    #   POST http://127.0.0.1:8000/payments/webhook/
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
