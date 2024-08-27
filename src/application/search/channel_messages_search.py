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
        messages = await self._client_pool.get().get_messages(
            self._channel_id, 
            count=self._max_message_count
        )
        # TODO Do search iteratively.
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
        return str(self._value)