import os
from src.application.client import ClientPool
from src.infrastructure.storage import Storage
from .search import Search
from .channel_messages_search import ChannelMessagesSearch, MessageFilter, AllMessageFilter

class MultiChannelMessagesSearch(Search):

    _client_pool: ClientPool = None
    _storage: Storage = None
    _channel_ids: list[str] = None
    _max_message_count: int = None
    _message_batch_size: int = 0
    _filter: MessageFilter = None
    _min_date: str = None
    _max_date: str = None

    def __init__(self, 
                 client_pool: ClientPool, 
                 storage: Storage, 
                 channel_ids: list[str], 
                 max_message_count: int,
                 message_batch_size: int,
                 min_date: str,
                 max_date: str,
                 filter: MessageFilter = AllMessageFilter(),
                ):
        self._client_pool = client_pool
        self._storage = storage
        self._channel_ids = channel_ids
        self._max_message_count = max_message_count
        self._message_batch_size = message_batch_size
        self._min_date = min_date
        self._max_date = max_date
        self._filter = filter

    async def start(self):
        for channel_id in self._channel_ids:
            search = ChannelMessagesSearch(
                client_pool=self._client_pool,
                storage=self._storage,
                channel_id=channel_id,
                max_message_count=self._max_message_count,
                message_batch_size=self._message_batch_size,
                min_date=self._min_date,
                max_date=self._max_date,
                filter=self._filter
            )
            await search.start()