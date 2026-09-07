from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_str):
    try:
        access_token = AccessToken(token_str)  # validează semnătura + expirarea
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except (TokenError, User.DoesNotExist, KeyError):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Populează scope['user'] pe baza tokenului JWT trimis ca query param
    la conectarea WebSocket, ex:
        ws://localhost:8000/ws/reviews/5/?token=<access_token>

    Înlocuiește AuthMiddlewareStack (care e bazat pe sesiune/cookie și
    nu are cum să recunoască userii autentificați prin JWT din React).
    """

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]

        scope['user'] = await get_user_from_token(token) if token else AnonymousUser()

        return await super().__call__(scope, receive, send)