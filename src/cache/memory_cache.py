from .cache import Cache


class MemoryCache(Cache):
    """
    In-memory cache implementation.
    """
    _storage = None

    def __init__(self):
        self._storage = {}

    def store(self, entity_type, entity_id, entity_value, ttl_seconds):
        # TODO ttl is not implemented
        if entity_type not in self._storage:
            self._storage[entity_type] = {}
        self._storage[entity_type][entity_id] = entity_value

    def get(self, entity_type, entity_id):
        if entity_type not in self._storage:
            self._storage[entity_type] = {}
        return self._storage[entity_type].get(entity_id, None)