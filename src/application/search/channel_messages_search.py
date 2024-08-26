from src.application.client import ClientPool
from src.infrastructure.storage import Storage, StoredItem
from src.infrastructure.telegram import Message


class ChannelMessagesSearch:
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
        messages = await self._client_pool.get().get_messages(self._channel_id, count=10)
        # TODO Do search iteratively.
        for message in messages:
            self._storage.save(StoredMessage(message))


class StoredMessage(StoredItem):
    
    def __init__(self, message: Message):
        self._value = {
            'id': message.message_id,
            'channel_id': message.channel_id,
            'text': message.text
        }    

    def get_type(self) -> str:
        return 'message'

    def get_key(self) -> str:
        return 'id'
        
    def get_value(self) -> dict[str, str]:
        return self._value