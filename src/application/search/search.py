from abc import ABC, abstractmethod

class Search(ABC):
    """
    Base class for search strategies.
    Search strategy is used to find which data should be stored.
    """

    @abstractmethod
    async def start():
        """
        Starts search.
        """
        pass