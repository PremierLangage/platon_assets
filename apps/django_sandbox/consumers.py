import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer



class SandboxUsageConsumer(WebsocketConsumer):
    sandbox_id: int
    sandbox_group_name: str
    
    
    def connect(self):
        self.sandbox_id = self.scope['url_route']['kwargs']['id']
        self.sandbox_group_name = 'sandbox_%s' % self.sandbox_id
        
        async_to_sync(self.channel_layer.group_add)(
            self.sandbox_group_name,
            self.channel_name
        )
        
        self.accept()
    
    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.sandbox_group_name,
            self.channel_name
        )
    
    
    def usage_data(self, event):
        self.send(text_data=json.dumps({
            'usage': event['usage']
        }))
