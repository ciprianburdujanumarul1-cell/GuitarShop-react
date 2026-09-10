# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'items_display', 'user', 'full_name', 'address_line1',
        'address_line2', 'city', 'postal_code', 'country',
        'amount_total', 'created_at',
    ]
    def items_display(self, obj):
        rows = "".join(
            f"<div style='white-space:nowrap;'>{name} × {qty}</div>"
            for name, qty in obj.items.items()
        )
        return format_html(rows)

    items_display.short_description = "Items"

    items_display.short_description = "Items"
    list_filter = ["country", "created_at"]
    search_fields = ["full_name", "stripe_session_id", "user__email"]
    readonly_fields = [f.name for f in Order._meta.fields]  # comenzile nu se editează manual