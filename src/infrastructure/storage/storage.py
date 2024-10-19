from abc import ABC, abstractmethod


class StoredItem(ABC):
    """
    Base class for all entities that can be stored.
    """

    @abstractmethod
    def get_type(self) -> str:
        """
        Returns
        -------
        str
            Returns type of the entity being stored. 
            Entities of same type should have same structure.
        """
        pass

    @abstractmethod
    def get_value(self) -> dict[str, str]:
        """
        Returns
        -------
        dict[str, str]
            Returns entity is a dict.
            If your entity is a complex object, you can use database normalization rules.
        """
        pass


class Storage(ABC):
    """
    This class is used to store collected data.
    """

    def save(self, item: StoredItem):
        """
        Saves entity to storage.

        Parameters
        ----------
        item: StoredItem
            Item to be stored. 

        Returns
        -------
        None
            Returns nothing.
        """
        pass

    def read(self, entity_type: str) -> str:
        pass