# admin.py
from django.contrib import admin
from .models import Userdetail

@admin.register(Userdetail)
class UserdetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'country', 'city', 'address', 'postal_code')
    search_fields = ('user__username', 'user__email', 'country', 'city')
    
    # Dacă ai păstrat câmpul email în Userdetail
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'