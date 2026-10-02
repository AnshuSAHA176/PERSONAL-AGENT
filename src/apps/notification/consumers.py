from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from apps.account.models import User

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        self.group_name = f"user-{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        

        await self.accept()

    async def disconnect(self, close_code):

        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_nam,
                self.channel_name
            )
