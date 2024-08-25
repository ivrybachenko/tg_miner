from src.logger import logger
from src.cache import Cache
from src.telegram import TelegramApi, TelethonTelegramApi


class Client:
    """
    Object which is used for API calls.
    """
    name: str = None
    is_active: bool = False
    _api: TelegramApi = None
    _cache: Cache = None

    def __init__(self, client_name, api_id, api_hash, cache):
        self._api = TelethonTelegramApi(client_name, api_id, api_hash, cache)
        self._cache = cache
        self.name = client_name

    async def activate(self):
        """
        Ensures that client is ready for API-calls. 
        Performs authorization if needed.
        """
        try:
            await self._api.authorize()
            self.is_active = True
        except Exception as e:
            self.is_active = False
            logger.info(f'Failed to activate Telegram client.')
    
    async def get_channel(self, channel_id):
        """
        Get channel by id.
        """
        return await self._api.get_channel(channel_id)
    
    async def get_messages(self, channel_id, *, count=3):
        """
        Get most recent messages from channel.
        """
        return await self._api.get_messages(channel_id, count)