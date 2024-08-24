from telethon import TelegramClient
from telethon.types import PeerChannel
from .logger import logger
from .cache import Cache

class Client:
    """
    Object which is used for API calls.
    """
    name: str = None
    is_active: bool = False
    _client = None
    _cache: Cache = None

    def __init__(self, client_name, api_id, api_hash, cache):
        self._client = TelegramClient(client_name, api_id, api_hash)
        self.name = client_name
        self._cache = cache


    async def activate(self):
        """
        Ensures that client is ready for API-calls. 
        Performs authorization if needed.
        """
        try:
            await self._client.start()
            async with self._client:
                me = await self._client.get_me()
                self.is_active = True
                logger.info(f'Telegram client activated. Username is {me.username}')
        except Exception as e:
            logger.info(f'Failed to activate Telegram client.')


    async def get_peer_id(self, channel_name):
        """
        Get channel_id by channel_name.
        """
        cached_value = self._cache.get('peer_id', channel_name)
        if cached_value is not None:
            return cached_value
        async with self._client:
            peer_id = await self._client.get_peer_id(channel_name)
            self._cache.store('peer_id', channel_name, peer_id, 60*60*24)
        return peer_id

    
    async def get_channel_by_name(self, channel_name):
        """
        Get channel by id.
        """
        channel_id = await self.get_peer_id(channel_name) 
        async with self._client:
            channel = await self._client.get_entity(PeerChannel(channel_id))
        return channel

    
    async def get_messages(self, channel_name, *, offset=0, count=3):
        """
        Get most recent messages from channel.
        """
        channel_id = await self.get_peer_id(channel_name)
        async with self._client:
            messages = await self._client.get_messages(
                entity=channel_id, 
                limit=count, 
                add_offset=offset
            )
        return messages