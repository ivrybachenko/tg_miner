class MemoryCache:
    """
    In-memory cache implementation.
    """
    # TODO extract interface
    # TODO test coverage is too low
    storage = {}


    def store(self, entity_type, entity_id, entity_value, ttl_seconds):
        """
        Stores the value in cache.
        """
        # TODO ttl is not implemented
        if entity_type not in self.storage:
            self.storage_api_key[entity_type] = {}
        self.storage[entity_type][entity_id] = entity_value

    
    def get(self, entity_type, entity_id):
        """
        Retrieves the value from cache.
        Returns None if value is not present or outdated.
        """
        if entity_type not in self.storage:
            self.storage_api_key[entity_type] = {}
        return self[entity_type].get(entity_id, None)