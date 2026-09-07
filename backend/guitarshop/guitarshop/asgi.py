import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guitarshop.settings')

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

import products.routing   # IMPORTANT FIX
from api.jwt_auth_middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": JWTAuthMiddleware(
        URLRouter(
            products.routing.websocket_urlpatterns
        )
    ),
})