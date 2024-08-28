from src.infrastructure.logging import logger
from src.infrastructure.cache import Cache
from src.infrastructure.telegram import TelegramApi


class Client:
    """
    Object which is used for API calls.
    """
    name: str = None
    is_active: bool = False
    _api: TelegramApi = None

    def __init__(self, client_name, api):
        self.name = client_name
        self.is_active = False
        self._api = api

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
            logger.error(f'Failed to activate Telegram client.\r\n{e}')
    
    async def get_channel(self, channel_id):
        """
        Get channel by id.
        """
        return await self._api.get_channel(channel_id)
    
    async def get_messages(self, channel_id, *, limit=3, offset_id=None, add_offset=None):
        """
        Get most recent messages from channel.
        """
        return await self._api.get_messages(channel_id, limit, offset_id, add_offset)