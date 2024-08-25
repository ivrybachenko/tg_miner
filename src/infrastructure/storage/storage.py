from abc import ABC, abstractmethod
from src.infrastructure.telegram import Channel, Message # TODO storage should use its own model

class Storage(ABC):
    """
    This class is used to store collected data.
    """
    
    @abstractmethod
    def save_message(self, message: Message):
        """
        Stores the message.

        Parameters
        ----------
        message: Message
            Message to store.

        Returns
        -------
        None
            Returns nothing.
        """
        pass

    @abstractmethod
    def save_channel(self, channel: Channel):
        """
        Stores the channel.

        Parameters
        ----------
        channel: Channel
            Channel to store.
        
        Returns
        -------
        None
            Returns nothing.
        """
        pass