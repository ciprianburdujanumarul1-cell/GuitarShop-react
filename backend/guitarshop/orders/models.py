from django.conf import settings
from django.db import models


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    stripe_session_id = models.CharField(max_length=255, unique=True)
    items = models.JSONField()  # {product_id: qty} — snapshot la momentul comenzii

    full_name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=2)

    vat_rate = models.DecimalField(max_digits=5, decimal_places=2)
    amount_total = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} — {self.full_name} ({self.stripe_session_id})"