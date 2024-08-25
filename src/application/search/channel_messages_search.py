from src.application.client import ClientPool


class ChannelMessagesSearch:
    """
    Downloads messages from Telegram channel.
    """
    _client_pool: ClientPool = None
    _channel_id: str = None
    _max_message_count: int = None

    def __init__(self, client_pool: ClientPool, channel_id: str, max_message_count: int):
        self._client_pool = client_pool
        self._channel_id = channel_id
        self._max_message_count = max_message_count

    async def start(self):
        messages = await self._client_pool.get().get_messages(self._channel_id, count=10)
        # TODO Do search iteratively.
        # TODO Should not return the whole list.
        return messages