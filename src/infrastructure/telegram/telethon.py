from telethon import TelegramClient
from telethon.types import PeerChannel
from .api import TelegramApi
from ..cache import Cache
from .model import Channel, Message


def get_client_factory():
    return TelegramClient


class TelethonTelegramApi(TelegramApi):
    """
    Implementation of Telegram API using Telethon library.
    """
    _cache: Cache
    _client: None
    _PEER_ID_CACHE_TYPE: str = 'peer_id'
    _PEER_ID_TTL_SECONDS: int = 60*60*24 # 1 day

    def __init__(self, client_name: str, api_id: int, api_hash: str, cache: Cache):
        """
        Constructor.

        Parameters
        ----------
        client_name: str
            Arbitrary string. 
            It is used in logging to differentiate which client is sending requests.
        api_id: int
            You can get this value from my.telegram.org.
        api_hash: str
            You can get this value from my.telegram.org.
        cache: Cache
            Cache to store temporal data.
        """
        self._client = get_client_factory()(client_name, api_id, api_hash)
        self._cache = cache

    async def authorize(self):
        await self._client.start()

    async def get_channel(self, channel_id: str) -> Channel:
        peer_id = await self._get_peer_id(channel_id) 
        async with self._client:
            channel = await self._client.get_entity(PeerChannel(peer_id))
        return Channel(channel_id, channel.title)

    async def get_messages(self, channel_id: str, count: int) -> list[Message]:
        peer_id = await self._get_peer_id(channel_id)
        async with self._client:
            messages = await self._client.get_messages(
                entity=peer_id, 
                limit=count
            )
        return [
            Message(
                x.id, 
                x.text
            )
            for x in messages
        ]

    async def _get_peer_id(self, channel_id: str):
        """
        Transforms channel_id to peer_id.

        Channel_id is a human-readable string which is used to identify channel.
        Peer_id is an unique identifier of channel which is used internally in Telegram.
        """
        cached_value = self._cache.get(self._PEER_ID_CACHE_TYPE, channel_id)
        if cached_value is not None:
            return cached_value
        async with self._client:
            peer_id = await self._client.get_peer_id(channel_id)
            self._cache.store(
                entity_type=self._PEER_ID_CACHE_TYPE, 
                entity_id=channel_id, 
                entity_value=peer_id, 
                ttl_seconds=self._PEER_ID_TTL_SECONDS
            )
        return peer_id