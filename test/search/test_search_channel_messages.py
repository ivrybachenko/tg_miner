import unittest
import asyncio
import json
from mockito import mock, verify, when, verifyNoMoreInteractions
from src.infrastructure.storage import ConsoleStorage
from src.infrastructure.cache import MemoryCache
from src.application.search import ChannelMessagesSearch
from src.application.search.channel_messages_search import StoredMessage
from src.application.client import ClientPool, Client
from test.utils import TelegramApiMock


def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


class TestChannelMessagesSearch(unittest.TestCase):

    async def create_search(self, storage, channels, limit):
        tg_mock = TelegramApiMock(channels)
        when(storage).save(any).thenCallOriginalImplementation()
        client_pool = ClientPool()
        client_pool.add_client(
            Client(
                client_name="client_1",
                api=tg_mock,
                cache=MemoryCache()
            )
        )
        await client_pool.activate_clients()
        return ChannelMessagesSearch(
            channel_id='channel_1',
            client_pool=client_pool,
            storage=storage,
            max_message_count=limit
        )

    @async_test
    async def test_limit_is_equal_to_message_count(self):
        storage_mock = mock(ConsoleStorage)
        search = await self.create_search(
            storage_mock,
            ['test/resources/search/channel_messages/before/channel_1.json'],
            limit=5
        )
        await search.start()
        self.verify_storage(
            storage_mock,
            'test/resources/search/channel_messages/after/messages_all.json'
        )
    
    @async_test
    async def test_limit_is_less_than_message_count(self):
        storage_mock = mock(ConsoleStorage)
        search = await self.create_search(
            storage_mock,
            ['test/resources/search/channel_messages/before/channel_1.json'],
            limit=3
        )
        await search.start()
        self.verify_storage(
            storage_mock,
            'test/resources/search/channel_messages/after/messages_1_2_3.json'
        )
    
    @async_test
    async def test_limit_is_more_than_message_count(self):
        storage_mock = mock(ConsoleStorage)
        search = await self.create_search(
            storage_mock,
            ['test/resources/search/channel_messages/before/channel_1.json'],
            limit=6
        )
        await search.start()
        self.verify_storage(
            storage_mock,
            'test/resources/search/channel_messages/after/messages_all.json'
        )

    def verify_storage(self, storage, expected_messages):
        expected_messages = self.read_expected_messages(
            expected_messages
        )
        for m in expected_messages:
            verify(storage).save(m)
        verifyNoMoreInteractions(storage)        

    def read_expected_messages(self, filename):
        with open(filename, 'r') as f:
            content = f.read()
            messages = json.loads(content)
            return [
                StoredMessage(m)
                for m in messages
            ]