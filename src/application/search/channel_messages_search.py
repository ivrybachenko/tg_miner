from src.application.client import ClientPool
from src.infrastructure.storage import Storage, StoredItem
from src.infrastructure.telegram import MessageResponse
from .search import Search


class ChannelMessagesSearch(Search):
    """
    Downloads messages from Telegram channel.
    """
    _client_pool: ClientPool = None
    _storage: Storage = None
    _channel_id: str = None
    _max_message_count: int = None
    _error_id: int = 0

    def __init__(self, client_pool: ClientPool, 
                        storage: Storage, 
                        channel_id: str, 
                        max_message_count: int
                ):
        self._client_pool = client_pool
        self._storage = storage
        self._channel_id = channel_id
        self._max_message_count = max_message_count

    async def start(self):
        # TODO Do search iteratively.
        try:
            messages = await self._client_pool.get().get_messages(
                self._channel_id, 
                count=self._max_message_count
            )
        except Exception as e:
            messages = []
            self._storage.save(StoredGetMessageError(
                self._error_id, 
                self._channel_id,
                self._max_message_count, 
                e
            ))
            self._error_id = self._error_id + 1
        for message in messages:
            self._storage.save(StoredMessage(message))


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
    
    def __init__(self, error_id, channel_id, max_message_count, ex):
        self._value = {
            'id': str(error_id),
            'channel_id': str(channel_id),
            'max_message_count': str(max_message_count),
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