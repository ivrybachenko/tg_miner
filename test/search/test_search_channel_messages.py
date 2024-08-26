import unittest
import asyncio
from mockito import mock, verify
from src.infrastructure.storage import Storage
from src.infrastructure.cache import MemoryCache
from src.application.search import ChannelMessagesSearch
from src.application.client import ClientPool, Client
from test.utils import TelegramMocker


def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


class TestChannelMessagesSearch(unittest.TestCase):
    @async_test
    async def test_save_all_messages(self):
        tg_mock = TelegramMocker()
        tg_mock.add_channel('test/resources/channel_1.json')
        storage_mock = mock(Storage)
        client_pool = ClientPool()
        client_pool.add_client(
            Client(
                client_name="client_1",
                api=tg_mock.get(),
                cache=MemoryCache()
            )
        )
        await client_pool.activate_clients()
        search = ChannelMessagesSearch(
            channel_id='channel_1',
            client_pool=client_pool,
            storage=storage_mock,
            max_message_count=10
        )
        await search.start()
        verify(storage_mock.save(any))