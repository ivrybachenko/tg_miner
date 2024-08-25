import configparser
from src.logger import logger
from .client import Client
from src.cache import MemoryCache


class ClientPool:
    """
    Responsible for managing a client pool.
    """
    _clients = [] # All registered clients
    _next_client_index = 0 # Id of client which will be used for API call next time
    _cache = MemoryCache()

    def read_clients_from_properties(self, properties_file):
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
        client_config.read(properties_file)
        for client_name in client_config.sections():
            api_id = client_config.get(client_name, 'api_id')
            api_hash = client_config.get(client_name, 'api_hash')
            client = Client(client_name, api_id, api_hash, self._cache)
            self._clients.append(client)

    def get_active_clients(self):
        """
        Returns the list of active clients.
        """
        return [x for x in self._clients if x.is_active]
    
    async def activate_clients(self):
        """
        Ensures that each client is ready for API calls. 
        """
        logger.info('Activating Telegram clients...')
        total_count = len(self._clients)
        for i, client in enumerate(self._clients):
            logger.info(f'Activating Telegram client {i+1}/{total_count}: {client.name}')
            await client.activate()
        count_active = len([x for x in self._clients if x.is_active])
        logger.info('Activating Telegram clients finished.')
        logger.info(f'Successfully activated {count_active} of {total_count} clients.')
        logger.info([
            {
                'name': client.name, 
                'is_active': client.is_active
            } 
            for client in self._clients
        ])
        
    def get(self):
        """
        Returns the next client which can be used for API call.
        """
        active_clients = self.get_active_clients()
        if len(active_clients) == 0:
            raise Exception('No active clients available.')
        next_client = active_clients[self._next_client_index]
        self.next_client_index = (self._next_client_index + 1) % len(active_clients)
        return next_client
