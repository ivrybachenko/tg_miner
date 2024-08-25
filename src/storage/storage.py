from abc import ABC, abstractmethod
from src.telegram import Channel, Message

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