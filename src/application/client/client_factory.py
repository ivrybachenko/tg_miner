import configparser
from src.infrastructure.cache import MemoryCache
from src.infrastructure.logging import logger
from .client import Client

class ClientFactory:
    """
    Set of methods to create a new client.
    """
    _cache = MemoryCache()

    def read_clients_from_properties(self, filename):
        """
        Reads list of clients from property file.
        
        Property file should have the following structure:
        [CLIENT_TITLE_1]
        api_id=242563869
        api_hash=ceb789345d95101f1245a607277f4563
        [CLIENT_TITLE_1]
        api_id=73033868
        api_hash=jio789345d95101f1245a607277f4563
        """
        logger.info('Reading client list from properties...')
        client_config = configparser.ConfigParser()
        client_config.read(filename)
        clients = []
        for client_name in client_config.sections():
            api_id = client_config.get(client_name, 'api_id')
            api_hash = client_config.get(client_name, 'api_hash')
            client = Client(client_name, api_id, api_hash, self._cache)
            clients.append(client)
        return clients