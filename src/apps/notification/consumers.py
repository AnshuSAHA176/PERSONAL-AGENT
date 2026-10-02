from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from apps.account.models import User

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]

        self.group_name = f"user-{self.user.id}"
        if not self.user.is_authenticated:
            await self.close()
            return


        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        print(f'CONNECT {self.group_name}')
        

        await self.accept()

    async def disconnect(self, close_code):

        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_nam,
                self.channel_name
            )
    async def notification(self,event):
        print(f'CONNECT {self.user.id}')
        await self.send(text_data=json.dumps({
            "type": "notification_message",
            "message": event["message"],
        }))