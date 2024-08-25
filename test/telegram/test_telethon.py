import unittest
import asyncio
from mockito import mock, when, verify, verifyNoMoreInteractions
from telethon.types import PeerChannel
import src.telegram.telethon as tg_telethon
from src.telegram import TelethonTelegramApi, Channel, Message
from src.cache import MemoryCache

def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


class TestTelethonTelegramApi(unittest.TestCase):

    def create_tg_mock(self):
        tg_mock = mock()
        when(tg_mock).__call__(any, any, any).thenReturn(tg_mock)
        when(tg_mock).__aenter__().thenReturn(self.f_result(tg_mock))
        when(tg_mock).__aexit__(any,any,any).thenReturn(self.f_result(tg_mock))
        when(tg_telethon)\
            .get_client_factory()\
            .thenReturn(tg_mock)
        return tg_mock

    def f_empty(self):
        f = asyncio.Future()
        f.set_result(None)
        return f

    def f_result(self, result):
        f = asyncio.Future()
        f.set_result(result)
        return f
    
    def f_raise(self, exception):
        f = asyncio.Future()
        f.set_exception(exception)
        return f

    @async_test
    async def test_authorize_success(self):
        tg_mock = self.create_tg_mock()
        when(tg_mock).start().thenReturn(self.f_empty())

        api = TelethonTelegramApi('client_name', 12762, 'api_hash', MemoryCache())
        await api.authorize()

        verify(tg_mock).__call__('client_name', 12762, 'api_hash')
        verify(tg_mock).start()
        verifyNoMoreInteractions(tg_mock)

    @async_test
    async def test_authorize_failed(self):
        tg_mock = self.create_tg_mock()
        when(tg_mock).start().thenReturn(self.f_raise(Exception('Auth failed')))

        api = TelethonTelegramApi('client_name', 12762, 'api_hash', MemoryCache())
        with self.assertRaises(Exception):
            await api.authorize()

        verify(tg_mock).__call__('client_name', 12762, 'api_hash')
        verify(tg_mock).start()
        verifyNoMoreInteractions(tg_mock)

    @async_test
    async def test_get_channel(self):
        expected_channel = Channel('channel_id', 'channel_title')
        peer_id = 'peer_id'
        tg_mock = self.create_tg_mock()
        when(tg_mock).get_peer_id(expected_channel.id).thenReturn(self.f_result(peer_id))
        when(tg_mock).get_entity(PeerChannel(peer_id)).thenReturn(self.f_result(expected_channel))
        
        api = TelethonTelegramApi('client_name', 12762, 'api_hash', MemoryCache())
        await api.get_channel(expected_channel.id)

        verify(tg_mock).__call__('client_name', 12762, 'api_hash')
        verify(tg_mock, times=2).__aenter__()
        verify(tg_mock, times=2).__aexit__(any, any, any)
        verify(tg_mock).get_peer_id(expected_channel.id)
        verify(tg_mock).get_entity(PeerChannel(peer_id))
        verifyNoMoreInteractions(tg_mock)

    @async_test
    async def test_get_channel_use_cached_peer_id(self):
        expected_channel = Channel('channel_id', 'channel_title')
        peer_id = 'peer_id'
        tg_mock = self.create_tg_mock()
        when(tg_mock).get_peer_id(expected_channel.id).thenReturn(self.f_result(peer_id))
        when(tg_mock).get_entity(PeerChannel(peer_id)).thenReturn(self.f_result(expected_channel))
        
        api = TelethonTelegramApi('client_name', 12762, 'api_hash', MemoryCache())
        await api.get_channel(expected_channel.id)
        await api.get_channel(expected_channel.id)

        verify(tg_mock).__call__('client_name', 12762, 'api_hash')
        verify(tg_mock, times=3).__aenter__()
        verify(tg_mock, times=3).__aexit__(any, any, any)
        verify(tg_mock).get_peer_id(expected_channel.id)
        verify(tg_mock, times=2).get_entity(PeerChannel(peer_id))
        verifyNoMoreInteractions(tg_mock)

    @async_test
    async def test_get_message(self):
        channel_id = 'some_channel_id'
        excpected_messages = [Message(1, 'some_text')]
        peer_id = 'peer_id'
        tg_mock = self.create_tg_mock()
        when(tg_mock).get_peer_id(channel_id).thenReturn(self.f_result(peer_id))
        when(tg_mock).get_messages(
            entity=any, 
            limit=any
        ).thenReturn(self.f_result(excpected_messages))
        
        api = TelethonTelegramApi('client_name', 12762, 'api_hash', MemoryCache())
        await api.get_messages(channel_id, 3)

        verify(tg_mock).__call__('client_name', 12762, 'api_hash')
        verify(tg_mock, times=2).__aenter__()
        verify(tg_mock, times=2).__aexit__(any, any, any)
        verify(tg_mock).get_peer_id(channel_id)
        verify(tg_mock).get_messages(entity=any, limit=any)
        verifyNoMoreInteractions(tg_mock)

    @async_test
    async def test_get_message_use_cached_peer_id(self):
        channel_id = 'some_channel_id'
        excpected_messages = [Message(1, 'some_text')]
        peer_id = 'peer_id'
        tg_mock = self.create_tg_mock()
        when(tg_mock).get_peer_id(channel_id).thenReturn(self.f_result(peer_id))
        when(tg_mock).get_messages(
            entity=any, 
            limit=any
        ).thenReturn(self.f_result(excpected_messages))

        api = TelethonTelegramApi('client_name', 12762, 'api_hash', MemoryCache())
        await api.get_messages(channel_id, 3)
        await api.get_messages(channel_id, 3)
        
        verify(tg_mock).__call__('client_name', 12762, 'api_hash')
        verify(tg_mock, times=3).__aenter__()
        verify(tg_mock, times=3).__aexit__(any, any, any)
        verify(tg_mock).get_peer_id(channel_id)
        verify(tg_mock, times=2).get_messages(entity=any, limit=any)
        verifyNoMoreInteractions(tg_mock)


if __name__ == '__main__':
    unittest.main()