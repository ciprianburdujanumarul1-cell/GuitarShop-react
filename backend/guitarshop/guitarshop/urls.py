
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("api/", include("api.urls")),
    path("", include("mainpage.urls")),
    path("electric/", include("electricguitar.urls")),
    path("products/", include("products.urls", namespace="products")),
    path("acoustic/", include("acousticguitar.urls")),
    path("bass/", include("bassguitar.urls")),
    path("payments/", include("payments.urls")),
    path("cart/", include("cart.urls")),
    path("admin/", admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)