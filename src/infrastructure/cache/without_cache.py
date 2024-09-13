from src.infrastructure.logging import logger
from .cache import Cache

class WithoutCache(Cache):
    """
    Do not use cache.
    """

    def store(self, entity_type, entity_id, entity_value, ttl_seconds):
        pass

    def get(self, entity_type, entity_id):
        return None