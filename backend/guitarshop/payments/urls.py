from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]