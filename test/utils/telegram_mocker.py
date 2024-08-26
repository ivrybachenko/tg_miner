import json
from mockito import mock, when
from src.infrastructure.telegram import TelegramApi

class TelegramMocker:
    
    def __init__(self):
        self._mock: TelegramApi = mock(TelegramApi)
        when(self._mock.authorize()).thenReturn(self._f_result(None))

    def _f_result(self, result):
        f = asyncio.Future()
        f.set_result(result)
        return f
    
    def add_channel(self, filename):
        with open(filename, 'r') as f:
            stub = f.read()
            stub = json.loads(stub)
            channel = stub['channel']
            messages = stub['messages']
            when(self._mock.get_channel(channel.id)).thenReturn(channel)
            when(self._mock.get_messages(channel.id, any)).thenReturn(messages)

    def get(self) -> TelegramApi:
        return self._mock