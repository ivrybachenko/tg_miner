from abc import ABC, abstractmethod
from src.application.client import ClientPool
from src.infrastructure.storage import Storage, StoredItem
from src.infrastructure.telegram import MessageResponse
from src.infrastructure.logging import logger
from .search import Search


class MessageFilter(ABC):
    @abstractmethod
    def match(self, message: MessageResponse) -> bool:
        pass


class AllMessageFilter(MessageFilter):
    def match(self, message: MessageResponse) -> bool:
        return True


class KeywordMessageFilter(MessageFilter):

    _keywords = []

    def __init__(self, keywords: list[str]):
        self._keywords = [x.lower() for x in keywords]

    def match(self, message: MessageResponse) -> bool:
        if message.text is None:
            return False
        text_lower = message.text.lower()
        for kw in self._keywords:
            if kw in text_lower:
                return True
        return False


class ChannelMessagesSearch(Search):
    """
    Downloads messages from Telegram channel.
    """
    _client_pool: ClientPool = None
    _storage: Storage = None
    _channel_id: str = None
    _max_message_count: int = None
    _error_id: int = 0
    _message_batch_size: int = 0
    _filter: MessageFilter = None

    def __init__(self, 
                 client_pool: ClientPool, 
                 storage: Storage, 
                 channel_id: str, 
                 max_message_count: int,
                 message_batch_size: int,
                 filter: MessageFilter,
                ):
        self._client_pool = client_pool
        self._storage = storage
        self._channel_id = channel_id
        self._max_message_count = max_message_count
        self._message_batch_size = message_batch_size
        self._filter = filter

    async def start(self):
        offset_id=0
        add_offset=0
        total_messages=0
        while True:
            logger.info(f'Total messages: {total_messages}')
            result = await self._download_batch(self._message_batch_size, offset_id, add_offset)
            total_messages += result['size']
            if result['size'] == 0 or total_messages>=self._max_message_count:
                break
            offset_id = result['last_message_id']
    
    async def _download_batch(self, batch_size, offset_id, add_offset):
        try:
            messages = await self._client_pool.get().get_messages(
                self._channel_id, 
                limit=batch_size,
                offset_id=offset_id,
                add_offset=add_offset
            )
            stats = {
                'last_message_id': messages[-1].message_id,
                'size': len(messages)
            }
            messages = [m for m in messages if self._filter.match(m)]
            for message in messages:
                if message.text is not None:
                    message.text = message.text.replace('\n', r'\n')
                self._storage.save(StoredMessage(message))
            return stats
        except Exception as e:
            self._storage.save(StoredGetMessageError(
                self._error_id, 
                self._channel_id,
                batch_size, 
                offset_id,
                add_offset,
                e
            ))
            logger.error(e)
            self._error_id = self._error_id + 1
            return []


class StoredMessage(StoredItem):
    
    def __init__(self, message: MessageResponse|dict[str,str]):
        if isinstance(message, MessageResponse):
            self._value = {
                'id': message.message_id,
                'channel_id': message.channel_id,
                'text': message.text
            }
        elif isinstance(message, dict):
            self._value = {
                'id': message.get('id', None),
                'channel_id': message.get('channel_id', None),
                'text': message.get('text', None)
            }

    def get_type(self) -> str:
        return 'message'

    def get_key(self) -> str:
        return 'id'
        
    def get_value(self) -> dict[str, str]:
        return self._value
    
    def __eq__(self, other):
        if isinstance(other, StoredMessage):
            return self._value == other._value
        return False
    
    def __str__(self):
        return self.get_type() + '=' + str(self._value)


class StoredGetMessageError(StoredItem):
    
    def __init__(self, error_id, channel_id, limit, offset_id, add_offset, ex):
        self._value = {
            'error_id': str(error_id),
            'channel_id': str(channel_id),
            'limit': str(limit),
            'offset_id': str(offset_id),
            'add_offset': str(add_offset),
            'exception': str(ex)
        }

    def get_type(self) -> str:
        return 'get_message_error'

    def get_key(self) -> str:
        return 'error_id'
        
    def get_value(self) -> dict[str, str]:
        return self._value
    
    def __eq__(self, other):
        if isinstance(other, StoredGetMessageError):
            return self._value == other._value
        return False
    
    def __str__(self):
        return self.get_type() + '=' + str(self._value)