from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "country", "amount_total", "created_at"]
    list_filter = ["country", "created_at"]
    search_fields = ["full_name", "stripe_session_id", "user__email"]
    readonly_fields = [f.name for f in Order._meta.fields]  # comenzile nu se editează manual