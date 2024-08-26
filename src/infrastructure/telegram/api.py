from abc import ABC, abstractmethod
from .model import ChannelResponse, MessageResponse


class TelegramApi(ABC):
    """
    API to interact with Telegram.
    """

    @abstractmethod
    async def authorize(self):
        """
        Performs authorization.
        Phone number and verification code can be asked.

        Raises
        ------
        Exception
            If authorization failed.
        """
        pass

    @abstractmethod
    async def get_channel(self, channel_id: str) -> ChannelResponse:
        """
        Get information about the channel.

        Parameters
        ----------
        channel_id: str
            Channel identifier. 
            For example, if channel link is t.me/ali_baba, than :channel_id is ali_baba.

        Returns
        -------
        Channel
            Returns information about the channel with given name.
        """
        pass

    @abstractmethod
    async def get_messages(self, channel_id: str, count: int) -> list[MessageResponse]:
        """
        Get messages from the channel.

        Parameters
        ----------
        channel_id: str
            Channel identifier. 
            For example, if channel link is t.me/ali_baba, than :channel_id is ali_baba.
        count: int
            Count of messages to be retrieved.
        
        Returns
        -------
        list[Message]
            Returns list of messages from the channel.
        """
        pass