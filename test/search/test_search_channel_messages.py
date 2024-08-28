import unittest
import asyncio
import json
from mockito import mock, verify, when, verifyNoMoreInteractions, unstub
from src.infrastructure.storage import ConsoleStorage
from src.application.search import ChannelMessagesSearch
from src.application.search.channel_messages_search import StoredMessage, StoredGetMessageError
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

    def create_storage(self):
        storage = mock(ConsoleStorage)
        when(storage).save(any).thenCallOriginalImplementation()
        return storage

    def f_raise(self, exception):
        f = asyncio.Future()
        f.set_exception(exception)
        return f

    async def create_search(self, storage, tg_api, limit, batch_size):
        client_pool = ClientPool()
        client_pool.add_client(
            Client(
                client_name="client_1",
                api=tg_api
            )
        )
        await client_pool.activate_clients()
        return ChannelMessagesSearch(
            channel_id='channel_1',
            client_pool=client_pool,
            storage=storage,
            max_message_count=limit,
            message_batch_size=batch_size
        )

    @async_test
    async def test_limit_is_equal_to_message_count(self):
        storage = self.create_storage()
        search = await self.create_search(
            storage,
            TelegramApiMock(['test/resources/search/channel_messages/before/channel_1.json']),
            limit=5,
            batch_size=5
        )
        await search.start()
        self.verify_stored_messages(
            storage,
            'test/resources/search/channel_messages/after/messages_all.json'
        )
        verifyNoMoreInteractions(storage)        
        unstub()
    
    @async_test
    async def test_limit_is_less_than_message_count(self):
        storage = self.create_storage()
        search = await self.create_search(
            storage,
            TelegramApiMock(['test/resources/search/channel_messages/before/channel_1.json']),
            limit=3,
            batch_size=3
        )
        await search.start()
        self.verify_stored_messages(
            storage,
            'test/resources/search/channel_messages/after/messages_1_2_3.json'
        )
        verifyNoMoreInteractions(storage)        
        unstub()
    
    @async_test
    async def test_limit_is_more_than_message_count(self):
        storage = self.create_storage()
        search = await self.create_search(
            storage,
            TelegramApiMock(['test/resources/search/channel_messages/before/channel_1.json']),
            limit=6,
            batch_size=6
        )
        await search.start()
        self.verify_stored_messages(
            storage,
            'test/resources/search/channel_messages/after/messages_all.json'
        )
        verifyNoMoreInteractions(storage)        
        unstub()
        
    @async_test
    async def test_batch_size_is_used(self):
        storage = self.create_storage()
        search = await self.create_search(
            storage,
            TelegramApiMock(['test/resources/search/channel_messages/before/channel_1.json']),
            limit=5,
            batch_size=2
        )
        await search.start()
        self.verify_stored_messages(
            storage,
            'test/resources/search/channel_messages/after/messages_all.json'
        )
        verifyNoMoreInteractions(storage)        
        unstub()

    @async_test
    async def test_do_not_fall_on_api_exception(self):
        storage = self.create_storage()
        tg_api = mock(TelegramApiMock(['test/resources/search/channel_messages/before/channel_1.json']))
        when(tg_api).authorize().thenCallOriginalImplementation()
        when(tg_api).get_messages(any, any, any, any).thenRaise(Exception('GET_MESSAGE error'))
        search = await self.create_search(
            storage,
            tg_api,
            limit=6,
            batch_size=6
        )
        await search.start()
        self.verify_stored_errors(
            storage,
            'test/resources/search/channel_messages/after/api_errors.json'
        )
        verifyNoMoreInteractions(storage)  
        unstub()

    def verify_stored_errors(self, storage, expected_errors):
        expected_errors = self.read_expected_errors(
            expected_errors
        )
        for m in expected_errors:
            verify(storage).save(m)

    def verify_stored_messages(self, storage, expected_messages):
        expected_messages = self.read_expected_messages(
            expected_messages
        )
        for m in expected_messages:
            verify(storage).save(m)

    def read_expected_messages(self, filename):
        with open(filename, 'r') as f:
            content = f.read()
            messages = json.loads(content)
            return [
                StoredMessage(m)
                for m in messages
            ]

    def read_expected_errors(self, filename):
        with open(filename, 'r') as f:
            content = f.read()
            messages = json.loads(content)
            return [
                StoredGetMessageError(
                    channel_id=m['channel_id'],
                    error_id=m['error_id'],
                    ex=m['ex'],
                    limit=m['limit'],
                    offset_id=m['offset_id'],
                    add_offset=m['add_offset']
                )
                for m in messages
            ]