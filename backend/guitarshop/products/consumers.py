import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Review, Product

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.product_id = self.scope['url_route']['kwargs']['product_id']
        self.room_group_name = f"reviews_{self.product_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        rating = data.get('rating', 5)

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = 5
        if rating < 1 or rating > 5:
            rating = 5

        # The WebSocket handshake has no Django session when it originates
        # from the React app (auth is JWT, not cookie-based), so trust the
        # username the authenticated client sends instead of scope['user'].
        username = (data.get('username') or '').strip()
        if not username:
            user = self.scope["user"]
            username = user.username if user.is_authenticated else "Anonymous"

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
    def save_review(self, username, message, rating):
        Review.objects.create(
            product_id=self.product_id,
            username=username,
            message=message,
            rating=rating,
        )