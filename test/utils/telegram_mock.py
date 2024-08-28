import json
from src.infrastructure.telegram import TelegramApi, ChannelResponse, MessageResponse

class TelegramApiMock(TelegramApi):
    
    _channels = {}

    def __init__(self, channel_filenames):
        for f in channel_filenames:
            self.add_channel(f)

    async def authorize(self):
        return None

    async def get_channel(self, channel_id: str) -> ChannelResponse:
        return self._channels[channel_id]['channel']

    async def get_messages(self, channel_id: str, limit: int, offset_id, add_offset) -> list[MessageResponse]:
        messages = self._channels[channel_id]['messages']
        start_index = 0
        for i, m in enumerate(messages):
            if m.message_id == offset_id:
                start_index = i
        return messages[start_index:start_index+min(limit, add_offset)]
    
    def add_channel(self, filename):
        with open(filename, 'r') as f:
            stub = f.read()
            stub = json.loads(stub)
            channel = stub['channel']
            channel = ChannelResponse(
                channel_id=channel.get('id', None), 
                title=channel.get('title', None)
            )
            messages = stub['messages']
            messages = [
                MessageResponse(
                    message_id=m.get('id', None),
                    text=m.get('text', None),
                    channel_id=m.get('channel_id', None),
                    channel_fwd_from_id=m.get('channel_fwd_from_id', None),
                    datetime=m.get('datetime', None),
                    forwards=m.get('forwards', None),
                    views=m.get('views', None)
                )
                for m in messages
            ]
            self._channels[channel.channel_id] = {
                'channel': channel,
                'messages': messages
            }