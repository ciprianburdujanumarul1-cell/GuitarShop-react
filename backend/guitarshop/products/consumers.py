import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Review, Product


class ChatConsumer(AsyncWebsocketConsumer):
    MAX_MESSAGE_LENGTH = 1000  # aliniat cu ce vrei să permiți în UI

    async def connect(self):
        # Necesită autentificare JWT reală, populată de JWTAuthMiddleware
        # în asgi.py — vezi scope['user']. Nu mai avem încredere în nimic
        # trimis de client la acest pas.
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close(code=4001)  # 4001 = unauthorized (cod custom)
            return

        self.product_id = self.scope['url_route']['kwargs']['product_id']

        # Verificăm că produsul chiar există, altfel oricine ar putea crea
        # recenzii "orfane" cu un product_id inventat.
        product_exists = await self.product_exists(self.product_id)
        if not product_exists:
            await self.close(code=4004)  # 4004 = not found (cod custom)
            return

        self.room_group_name = f"reviews_{self.product_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # group_discard e sigur de apelat chiar dacă connect() a ieșit
        # devreme (room_group_name ar putea să nu existe încă).
        room_group_name = getattr(self, 'room_group_name', None)
        if room_group_name:
            await self.channel_layer.group_discard(room_group_name, self.channel_name)

    async def receive(self, text_data):
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close(code=4001)
            return

        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            return  # ignorăm silențios payload malformat

        message = (data.get('message') or '').strip()
        if not message:
            return  # nu salvăm recenzii goale

        if len(message) > self.MAX_MESSAGE_LENGTH:
            message = message[:self.MAX_MESSAGE_LENGTH]

        rating = data.get('rating', 5)
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = 5
        if rating < 1 or rating > 5:
            rating = 5

        # Username-ul vine EXCLUSIV din user-ul autentificat prin JWT,
        # niciodată din payload-ul trimis de client — asta previne
        # impersonarea altor useri sau a brand-ului.
        username = user.username

        await self.save_review(username, message, rating)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
                "rating": rating,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
            "username": event["username"],
            "rating": event["rating"],
        }))

    @database_sync_to_async
    def product_exists(self, product_id):
        return Product.objects.filter(id=product_id).exists()

    @database_sync_to_async
    def save_review(self, username, message, rating):
        Review.objects.create(
            product_id=self.product_id,
            username=username,
            message=message,
            rating=rating,
        )