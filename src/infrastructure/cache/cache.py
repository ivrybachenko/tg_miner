from abc import ABC, abstractmethod


class Cache(ABC):
    """
    This class is used to cache the values.
    """

    @abstractmethod
    def store(self, entity_type: str, entity_id, entity_value, ttl_seconds: int):
        """
        Stores the value in cache.

        Parameters
        ----------
        entity_type: str
            Type of the value being stored. For example, channel or user.
        entity_id: any 
            Identifier of the value being stored. 
            It can be a number or any arbitrary object.
        entity_value: any
            The value being stored. It can have any type.
        ttl_seconds: int
            How long the value is stored in cache.
            When TTL is exceeded the value is treated to be removed from cache.

        Returns
        -------
        None
            Returns nothing.
        """
        pass

    @abstractmethod
    def get(self, entity_type, entity_id):
        """
        Retrieves the value from cache.

        Parameters
        ----------
        entity_type: str
            Type of the value being stored. For example, channel or user.
        entity_id: any 
            Identifier of the value being stored. 
            It can be a number or any arbitrary object.

        Returns
        -------
        any
            Returns the value which was stored with specified :entity_type and :entity_id.
            The type of returned value is the same as was used when the value was stored.
        None
            Returns None if the value is not present in cache or outdated.
        """
        pass