# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

list = []
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        list.append(self)
        await self.accept()

        for client in list:
            await client.send(text_data=json.dumps({
            'message': "Новый клиент подключился"
        }))

    async def disconnect(self, close_code):
        list.remove(self)
        for client in list:
            await client.send(text_data=json.dumps({
            'message': "Клиент отключился"
        }))
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message == "close":
            await self.close()
            await self.disconnect(0)
            pass
        for client in list:
            await client.send(text_data=json.dumps({
            'message': message
        }))
        # await self.send(text_data=json.dumps({
        #     'message': message
        # }))
