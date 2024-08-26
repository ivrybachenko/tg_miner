from telethon import TelegramClient
from telethon.types import PeerChannel
import time
from .api import TelegramApi
from ..cache import Cache
from .model import ChannelResponse, MessageResponse
from src.infrastructure.logging import logger


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
    _CHANNEL_BY_PEER_ID_CACHE_TYPE: str = 'channel_by_peer_id'
    _CHANNEL_BY_PEER_ID_TTL_SECONDS: int = 60*60 # 1 hour

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

    async def get_channel(self, channel_id: str) -> ChannelResponse:
        peer_id = await self._get_peer_id(channel_id) 
        return await self._get_channel_by_peer_id(PeerChannel(peer_id))

    async def _get_channel_by_peer_id(self, peer_id: PeerChannel) -> ChannelResponse:
        cached_value = self._cache.get(self._CHANNEL_BY_PEER_ID_CACHE_TYPE, peer_id.channel_id)
        if cached_value is not None:
            return cached_value
        async with self._client:
            logger.info(f'GET_ENTITY_BY_PEER_ID: {peer_id.channel_id}')
            time.sleep(1)
            channel = await self._client.get_entity(peer_id)
        channel = ChannelResponse(channel.username, channel.title)
        self._cache.store(self._CHANNEL_BY_PEER_ID_CACHE_TYPE, peer_id.channel_id, channel, self._CHANNEL_BY_PEER_ID_TTL_SECONDS)
        return channel


    async def get_messages(self, channel_id: str, count: int) -> list[MessageResponse]:
        peer_id = await self._get_peer_id(channel_id)
        async with self._client:
            logger.info(f'GET_MESSAGES: {channel_id}')
            time.sleep(1)
            messages = await self._client.get_messages(
                entity=peer_id, 
                limit=count
            )
        # TODO Handle exceptions from Telegram. Some channels are forbidden for scraping. 
        return [
            MessageResponse(
                message_id=x.id, 
                text=x.text,
                channel_id=(await self._get_channel_by_peer_id(x.peer_id)).channel_id,
                datetime=x.date,
                views=x.views,
                forwards=x.forwards,
                channel_fwd_from_id=await self._get_channel_from_id(x)
            )
            for x in messages
        ]

    async def _get_channel_from_id(self, message):
        if message.fwd_from is None:
            return None
        if type(message.fwd_from.from_id) != PeerChannel:
            return None
        channel_from = await self._get_channel_by_peer_id(message.fwd_from.from_id)
        return channel_from.channel_id

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
            logger.info(f'GET_PEER_ID: {channel_id}')
            time.sleep(1)
            peer_id = await self._client.get_peer_id(channel_id)
            self._cache.store(
                entity_type=self._PEER_ID_CACHE_TYPE, 
                entity_id=channel_id, 
                entity_value=peer_id, 
                ttl_seconds=self._PEER_ID_TTL_SECONDS
            )
        return peer_id