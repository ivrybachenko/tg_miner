import unittest
from src.infrastructure.cache import MemoryCache


class TestMemoryCache(unittest.TestCase):

    def test_get_from_empty_cache_is_none(self):
        cache = MemoryCache()
        actual_value = cache.get('entity_type', 'entity_id')
        self.assertIsNone(actual_value)

    def test_store_and_get(self):
        cache = MemoryCache()
        stored_value = {'name': 'some_name', 'id': 'some_id'}
        cache.store('entity_type', 'entity_id', stored_value, 1000)
        actual_value = cache.get('entity_type', 'entity_id')
        self.assertEqual(actual_value, stored_value)

    def test_store_and_get_different_entity_id(self):
        cache = MemoryCache()
        stored_value = {'name': 'some_name', 'id': 'some_id'}
        cache.store('entity_type', 'entity_id_1', stored_value, 1000)
        actual_value = cache.get('entity_type', 'entity_id_2')
        self.assertIsNone(actual_value)
    
    def test_store_and_get_different_entity_type(self):
        cache = MemoryCache()
        stored_value = {'name': 'some_name', 'id': 'some_id'}
        cache.store('entity_type_1', 'entity_id', stored_value, 1000)
        actual_value = cache.get('entity_type_2', 'entity_id')
        self.assertIsNone(actual_value)

    def test_store_and_get_after_ttl(self):
        raise Exception('Not implemented')

if __name__ == '__main__':
    unittest.main()